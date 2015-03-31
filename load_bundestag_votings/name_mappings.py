import psycopg2

mapping = {
    "Beckmeyer, Uwe": "Beckmeyer, Uwe Karl",
    "Brandl, Reinhard": "Brandl, Dr. Reinhard",
    "Groß, Michael": "Groß, Michael Peter",
    "Lämmel, Andreas Gottfried": "Lämmel, Andreas G.",
    "Launert, Silke": "Launert, Dr. Silke",
    "Mattheis, Hildegard": "Mattheis, Hilde",
    "Nüßlein, Dr. jur. Georg": "Nüßlein, Dr. iur. Georg",
    "Pätzold, Dr. rer. pol. Martin": "Pätzold, Dr. Martin",
    "Schavan, Dr. Annette": "Schavan, Annette",
    "Schavan, Prof. Dr. Annette": "Schavan, Annette",
    "Scheuer, Dr. Andreas": "Scheuer, Andreas",
    "Verlinden, Julia": "Verlinden, Dr. Julia",
    "Bartz, Julia": "Obermeier, Julia",
    "Neskovic, Wolfgang": "Nešković, Wolfgang"
}

def apply_mapping_to_db(mapping, key, db_config):
    tbl_indiv = "bundestag_votings_individual"

    con = psycopg2.connect("""
            dbname='{db}'
            user='{user}'
            host='{host}'
            password='{pw}'
        """.format(**db_config))

    cur = con.cursor()
    cur.execute("update {} set name = %s where name = %s".format(tbl_indiv), (mapping[key], key))
    con.commit()

def map_name(name):
    name = name.strip()

    if name in mapping:
        return mapping[name]
    else:
        return name
