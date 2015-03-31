import requests
import bs4
import re
import psycopg2
import name_mappings as nm

def load_votings_data(n, db_config):
    html = download_html_for_voting(n)
    
    if html is None:
        return False

    data = extract_data_from_html(html)
    write_voting_data_to_db(data, db_config)

    return True

def download_html_for_voting(n):
    url = "https://bundestag.de/apps/na/na/fraktion.form?id={}&url=%2Fapps%2Fna%2Fna%2Ffraktion.form".format(n)
    res = requests.get(url)
    if res.status_code == 200:
        return res.content
    else:
        return None

def extract_data_from_html(html):
    soup = bs4.BeautifulSoup(html)

    # meta data
    meta = soup.find("div", class_="namentlichText")
    gs = re.search("([0-9.]{10})(.+)",meta.find("h2").text)
    date = gs.group(1)
    dps = re.search("([0-9]{2})\.([0-9]{2})\.([0-9]{4})", date)
    date = dps.group(3)+"-"+dps.group(2)+"-"+dps.group(1)
    title = gs.group(2)
    sub = re.sub("\r\n", ". ", meta.p.text)

    # individual votings
    vec_div_namentlichBlock = soup.find_all("div", class_="namentlichBlock")
    vec_li = []
    for div_namentlichBlock in vec_div_namentlichBlock:
        vec_li += div_namentlichBlock.find_all("li")

    votings_data = []
    for li in vec_li:
        a_title = li.a["title"]
        vote_parts = re.search("([^:]+):([^:]+):([^():]+)",a_title)
        votings_data.append({
                "type": type_voting(vote_parts.group(1)),
                "name": vote_parts.group(2).strip(),
                "party": vote_parts.group(3).strip()
            })

    voting = {"date":date, "title":title, "subtitle":sub, "votings":votings_data}

    return voting
    
def type_voting(str):
    if(str == "Mit ja abgestimmt"):
        return 1
    elif(str == "Mit nein abgestimmt"):
        return -1
    elif(str == "Enthalten"):
        return 0
    elif(str == "Nicht anwesend"):
        return -10
    else:
        error("uuups ... what's that?")

def write_voting_data_to_db(data, db_config):
    tbl_meta = "bundestag_votings_meta"
    tbl_indiv = "bundestag_votings_individual"

    term = 18

    con = psycopg2.connect("""
            dbname='{db}'
            user='{user}'
            host='{host}'
            password='{pw}'
        """.format(**db_config))

    cur = con.cursor()

    # insert meta data for voting
    cur.execute("insert into {} (date,title,subtitle,term) values (%s,%s,%s,%s) returning id".format(tbl_meta),
            (data["date"], data["title"], data["subtitle"], term))
    con.commit()
    id_meta = cur.fetchall()
    id_meta = id_meta[0][0]

    # create temporary table for voting
    tbl_temp = "temp_bundestag_voting_{}".format(id_meta)

    cur = con.cursor()
    cur.execute("""
        create table {} (
            name text, 
            party text, 
            type integer, 
            id_member integer,
            id_meta)
        """.format(tbl_temp))
    con.commit()

    insertable = ",".join(["('{}','{}',{},{})".format(v["name"],v["party"],v["type"],id_meta) for v in data["votings"]])

    cur.execute("insert into {} (name, party, type, id_meta) values {}".format(tbl_temp, vdx))
    con.commit()
   
    # add member-IDs to voters
    cur.execute("""
        update {} as t
            set id_member = m.id
            from bundestag_members m
            where m.name = t.name
        """.format(tbl_temp))
    con.commit()

    # Activate only after manual checking for the first few times
    # cur.execute("""
    #         insert into {0} (id_meta, id_member, party, type) 
    #         select id_meta, id_member, party, type from {1}
    #     """.format(tbl_indiv, tbl_temp))
    # con.commit()
