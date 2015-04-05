select
    t.party,
    t.party_code,
    t.id_meta,
    t.date,
    t.n_yes,
    t.n_no,
    t.n_huh,
    t.n_gone,
    round(1.0*(t.n_yes - t.n_no) / (t.n_yes + t.n_no + t.n_huh),2) as opinion,
    round(t.unanimity,2) as unanimity,
    t.title,
    t.subtitle
    
from (
    select
        party.name as party,
        party.code as party_code,
        meta.id as id_meta,
        meta.date as date,
        meta.title as title,
        meta.subtitle as subtitle,

        stddev(case when indiv.type = -10 then NULL else indiv.type end) as unanimity,

        sum(case when indiv.type = 1   then 1 else 0 end) as n_yes,
        sum(case when indiv.type = 0   then 1 else 0 end) as n_huh,
        sum(case when indiv.type = -1  then 1 else 0 end) as n_no,
        sum(case when indiv.type = -10 then 1 else 0 end) as n_gone
        
    from bundestag_votings_individual indiv
    join bundestag_votings_meta meta
        on meta.id = indiv.id_meta
    join bundestag_members mems
        on mems.id = indiv.id_member
    join bundestag_parties party
        on party.id = indiv.id_party
    where
        meta.term = 18

    group by party.name, party.code, meta.id
    order by id_meta, party asc
) t

order by unanimity desc