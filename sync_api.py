#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_api.py — Sincroniza los equipos estacionarios desde la API pública de OPS
hacia el archivo de datos del parte (equipos.json).

Qué hace:
  1) Consulta  GET https://gestion.opssrlapp.com/api/public/v3/data/equipos-estacionarios
     (paginado), con el header X-API-Key.
  2) Filtra las 17 tareas del parte y clasifica los martillos hidráulicos (percutores).
  3) Reescribe equipos.json con: codigo, familia, tarea, marcaModelo, propietario,
     estadoBase, ubicacionBase y opsUpdatedAt (fecha del dato en la app de OPS).
  4) Deja un backup del equipos.json anterior y un sync_log.txt.

La API key NO se guarda en este archivo. Se toma (en este orden) de:
    --key <clave>   |   variable de entorno OPS_API_KEY   |   --key-file <ruta>
  y por defecto del apikey.txt del proyecto de Mantenimiento.

Uso:
    python sync_api.py                 # usa la key por defecto y escribe equipos.json al lado
    python sync_api.py --dry-run       # consulta pero NO escribe (muestra resumen)
    python sync_api.py --out otro.json # escribe en otra ruta

IMPORTANTE: después de correr esto, hay que volver a publicar la app en Claude con el
equipos.json actualizado (ver LEEME.txt). La app publicada no puede llamar la API por sí
misma (sandbox), por eso la sincronización corre acá afuera.
"""
import sys, os, json, time, argparse, datetime, urllib.request, urllib.error, urllib.parse

BASE = "https://gestion.opssrlapp.com"
ENDPOINT = "/api/public/v3/data/equipos-estacionarios"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_KEY_FILE = r"C:\Users\eramirez\OneDrive - Oilfield Production Services\Trabajo OPS\00 - Programa Mantenimiento\API TALLER\apikey.txt"

TASKS = {
    'GENERADORES','TORRE DE ILUMINACION','MOTOCOMPRESORES','ZAPATO COMPACTADOR','MOTOSOLDADORA',
    'ZARANDA','CHULENGO','PERFORADORA','AGUILONES','RODILLO COMPACTADOR','COMPACTADORA DE SUELO',
    'MOTOBOMBA','UÑA','CORTADORA DE CERAMICOS','ACABADO LISO Y NIVELADO','ESCARIFICADOR',
}

def norm(x): return str(x).strip().upper() if x is not None else ''
def s(x): return str(x).strip() if x is not None else ''

def is_hidraulico(dom):
    d = norm(dom)
    return ('HIDRAULICO' in d) or d.startswith('MARTILLO CATER') or d.startswith('MARTILLO INDECO') or d.startswith('MARTILLO STANLEY')

def get_key(args):
    if args.key: return args.key.strip()
    if os.environ.get('OPS_API_KEY'): return os.environ['OPS_API_KEY'].strip()
    kf = args.key_file or DEFAULT_KEY_FILE
    with open(kf, encoding='utf-8') as f:
        return f.read().strip()

def fetch_all(key, limit, timeout, retries, log):
    items = []
    page = 1
    while True:
        url = BASE + ENDPOINT + '?' + urllib.parse.urlencode({'page': page, 'limit': limit})
        req = urllib.request.Request(url, headers={'X-API-Key': key, 'Accept': 'application/json'})
        attempt = 0
        while True:
            attempt += 1
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    raw = r.read().decode('utf-8', 'replace')
                payload = json.loads(raw)
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode('utf-8', 'replace') if hasattr(e, 'read') else ''
                code = e.code
                # El servidor devuelve la SPA (HTML) cuando la ruta/versión no está publicada para la key
                if body.lstrip().startswith('<'):
                    raise SystemExit("[ERROR] La API respondió la pagina web (HTML), no JSON. "
                                     "Probablemente la version del endpoint cambió o la key no tiene permiso "
                                     "sobre la revision v3. Pedir habilitacion a Tecfield.")
                if code in (500, 502, 503, 504) and attempt <= retries:
                    log(f"  pagina {page}: HTTP {code} (intento {attempt}/{retries}); reintentando...")
                    time.sleep(2 * attempt); continue
                raise SystemExit(f"[ERROR] HTTP {code} en pagina {page}: {body[:300]}")
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt <= retries:
                    log(f"  pagina {page}: {e} (intento {attempt}/{retries}); reintentando...")
                    time.sleep(2 * attempt); continue
                raise SystemExit(f"[ERROR] No se pudo conectar en pagina {page}: {e}")
        data = payload.get('data', []) or []
        meta = payload.get('meta', {}) or {}
        items.extend(data)
        log(f"  pagina {page}: {len(data)} registros (total informado: {meta.get('total')})")
        if not meta.get('hasMore') or not data:
            break
        page += 1
        if page > (meta.get('totalPaginas') or 10000) + 1:
            break
    return items

def build(items, log):
    out = []
    descartados = 0
    for it in items:
        tarea = norm(it.get('tarea'))
        dom = s(it.get('dominio'))
        if tarea == 'PERCUTOR':
            if not is_hidraulico(dom):
                descartados += 1; continue
            label = 'MARTILLO HIDRAULICO'
        elif tarea in TASKS:
            label = tarea
        else:
            descartados += 1; continue
        mm = ' - '.join([p for p in [s(it.get('marca')), s(it.get('modelo'))] if p])
        ubic = s(it.get('ubicacionNombre')) or s(it.get('ubicacion'))
        out.append({
            'id': dom if dom else ('NUMEQ-' + str(it.get('numEquipo'))),
            'codigo': dom,
            'familia': s(it.get('familia')),
            'tarea': label,
            'marcaModelo': mm,
            'propietario': s(it.get('propietario')),
            'estadoBase': s(it.get('estado')),
            'ubicacionBase': ubic,
            'opsObservacion': s(it.get('observacion')),
            'opsUpdatedAt': it.get('updatedAt') or None,
        })
    # ids unicos
    seen = {}
    for d in out:
        k = d['id']
        if k in seen:
            seen[k] += 1; d['id'] = f"{k}#{seen[k]}"
        else:
            seen[k] = 1
    out.sort(key=lambda x: (x['tarea'], x['codigo']))
    log(f"  recibidos: {len(items)} · incluidos: {len(out)} · descartados (otras tareas): {descartados}")
    return out

def main():
    ap = argparse.ArgumentParser(description='Sincroniza equipos estacionarios desde la API de OPS.')
    ap.add_argument('--key'); ap.add_argument('--key-file')
    ap.add_argument('--out', default=os.path.join(HERE, 'equipos.json'))
    ap.add_argument('--limit', type=int, default=200)
    ap.add_argument('--timeout', type=int, default=60)
    ap.add_argument('--retries', type=int, default=3)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    loglines = []
    def log(m):
        print(m); loglines.append(m)
    log(f"=== Sync estacionarios OPS · {ts} ===")
    try:
        key = get_key(args)
    except Exception as e:
        log(f"[ERROR] No se pudo leer la API key: {e}"); sys.exit(2)

    items = fetch_all(key, args.limit, args.timeout, args.retries, log)
    data = build(items, log)

    if not data:
        log("[ATENCION] La API respondio pero no quedaron equipos tras el filtro. No se escribe nada.")
        sys.exit(3)

    if args.dry_run:
        from collections import Counter
        c = Counter(d['tarea'] for d in data)
        log("  (dry-run) por tarea: " + ', '.join(f"{k}={v}" for k, v in sorted(c.items())))
        log("  (dry-run) no se escribio equipos.json.")
    else:
        out = args.out
        if os.path.exists(out):
            bak = out.replace('.json', '') + '_backup_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.json'
            try:
                os.replace(out, bak); log(f"  backup del anterior: {os.path.basename(bak)}")
            except Exception as e:
                log(f"  [aviso] no se pudo hacer backup: {e}")
        tmp = out + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, out)
        log(f"  OK escrito: {out} ({len(data)} equipos)")
        log("  Siguiente paso: volver a publicar la app en Claude con este equipos.json (ver LEEME.txt).")

    try:
        with open(os.path.join(HERE, 'sync_log.txt'), 'a', encoding='utf-8') as f:
            f.write('\n'.join(loglines) + '\n\n')
    except Exception:
        pass

if __name__ == '__main__':
    main()
