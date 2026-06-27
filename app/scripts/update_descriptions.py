"""Update meta_config.yaml descriptions with actual DB dimension values."""

import pymysql
from pathlib import Path
from omegaconf import OmegaConf

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DB_HOST = "192.168.10.150"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "123321"
DB_NAME = "finance"

conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = conn.cursor()

config_path = ROOT_DIR / "conf" / "meta_config.yaml"
raw = OmegaConf.load(config_path)

for table_cfg in raw.tables:
    for col_cfg in table_cfg.columns:
        if col_cfg.role != "dimension":
            continue
        try:
            sql = f"SELECT DISTINCT `{col_cfg.name}` FROM `{table_cfg.name}` WHERE `{col_cfg.name}` IS NOT NULL LIMIT 50"
            cursor.execute(sql)
            rows = [str(row[0]) for row in cursor.fetchall()]
            if rows:
                existing_desc = col_cfg.description if col_cfg.description else col_cfg.name
                values_str = "/".join(rows[:20])
                col_cfg.description = f"{existing_desc.split('：')[0] if '：' in existing_desc else existing_desc}，可选值：{values_str}"
        except Exception:
            pass

conn.close()

OmegaConf.save(raw, config_path)
print(f"Updated {config_path}")