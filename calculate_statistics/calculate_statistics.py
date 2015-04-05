import psycopg2
import pandas as pd
import csv
import re

def read_query_from_file(fname):
    q = open(fname).read()
    q = " ".join(q.split()).replace(u'\ufeff', '')
    return q

def aggregated_votings_by_members(con):
    subject = "aggregated_votings_by_member"

    query = read_query_from_file("sql/{}.sql".format(subject))

    cur = con.cursor()
    cur.execute(query)
    con.commit()
    res = cur.fetchall()
    
    df = pd.DataFrame(res, columns=["party","party_code","name","profile_url","yes","huh","no","gone"])
    df["n_ynh"] = df.yes + df.no + df.huh
    df["g_per_ynhg"] = df.gone / (df.yes + df.no + df.huh + df.gone)
    df["h_per_ynh"] = df.huh / (df.yes + df.no + df.huh)

    df.to_csv("data/{}.csv".format(subject), index=False, quoting=csv.QUOTE_NONNUMERIC)
   
    top_n = 30

    # individual absence
    df = df.sort("g_per_ynhg", ascending=False)
    dfx = df[["party","party_code","name","profile_url","yes","huh","no","gone","g_per_ynhg"]][0:top_n]
    dfx["g_per_ynhg"] = dfx["g_per_ynhg"].apply(lambda r: round(r,2))
    json_str = dfx.to_json(orient="records", force_ascii=False)
    open("data/{}_absence.js".format(subject),"w").write("var data_{}_absence = {}".format(subject,json_str))

    # individual neutrality
    df = df.sort("h_per_ynh", ascending=False)
    dfx = df[["party","party_code","name","profile_url","yes","huh","no","gone","h_per_ynh"]][0:top_n]
    dfx["h_per_ynh"] = dfx["h_per_ynh"].apply(lambda r: round(r,2))
    json_str = dfx.to_json(orient="records", force_ascii=False)
    open("data/{}_neutrality.js".format(subject),"w").write("var data_{}_neutrality = {}".format(subject,json_str))


def party_opinion(con):
    subject = "party_opinion"

    query = read_query_from_file("sql/{}.sql".format(subject))

    cur = con.cursor()
    cur.execute(query)
    con.commit()
    res = cur.fetchall()

    df = pd.DataFrame(res, columns=[
        "party","code","id_meta","date","n_yes","n_no","n_huh","n_gone",
        "opinion", "unanimity", "title", "subtitle"
    ])

    df = df.sort("unanimity",ascending=False)
    df.to_csv("data/{}.csv".format(subject), index=False, quoting=csv.QUOTE_NONNUMERIC)
    
    top_n = 50
    dfx = df[0:top_n]

    # applies to each subtitle the replacement of a printed matter ID with an
    # according html anchor
    dfx.subtitle = dfx.subtitle.apply(lambda text: re.sub("(\d+)/(\d+)(\d{2})", lambda m: abc_to_anchor(m.groups(1)), text))
    
    json_str = dfx.to_json(orient="records", force_ascii=False)

    open("data/{}.js".format(subject),"w").write("var data_{} = {}".format(subject,json_str))



def deviation_from_party_opinion(con):
    subject = "deviation_from_party_opinion"

    query = read_query_from_file("sql/{}.sql".format(subject))

    cur = con.cursor()
    cur.execute(query)
    con.commit()
    res = cur.fetchall()

    df = pd.DataFrame(res, columns=["id_member","party","party_code","name","profile_url","diff","n"])
    df = df.sort("diff",ascending=False)

    df.to_csv("data/{}.csv".format(subject), index=False, quoting=csv.QUOTE_NONNUMERIC)

    top_n = 100
    dfx = df[["name","profile_url","party","party_code","diff"]][0:top_n]
    dfx = dfx.rename(columns={"party_code":"code", "diff":"score"})

    json_str = dfx.to_json(orient="records", force_ascii=False)

    open("data/{}.js".format(subject),"w").write("var data_{} = {}".format(subject,json_str))





def create_default_con():
    con = psycopg2.connect("""
            dbname='data' user='postgres' password='postgres' host='localhost'
        """)
    return con


def abc_to_anchor(abc):
    a,b,c = (int(x) for x in abc)
    url = "http://dip21.bundestag.de/dip21/btd/{0:}/{1:03d}/{0:}{1:03d}{2:02d}.pdf".format(a,b,c)
    a = "<a href='{3:}' target='printed_matter'>{0:}{1:}{2:02d}</a>".format(a,b,c,url)
    return a
