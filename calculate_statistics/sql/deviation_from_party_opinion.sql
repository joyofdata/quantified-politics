select
    indiv.id_member as id_member,
    party.name as party,
    party.code as party_code,
    mems.name as name,
    mems.bundestag_profile_url as profile_url,
    round(avg(abs(indiv.type - s.opinion)),2) as diff,
    count(*) as n
    
from bundestag_votings_individual as indiv
join (
    select
        t.id_party,
        t.id_meta,
        1.0*(n_yes - n_no) / (n_yes + n_no + n_gone) as opinion
        
    from (
        select
            mems.id_party as id_party,
            meta.id as id_meta,

            sum(case when indiv.type = 1   then 1 else 0 end) as n_yes,
            sum(case when indiv.type = 0   then 1 else 0 end) as n_huh,
            sum(case when indiv.type = -1  then 1 else 0 end) as n_no,
            sum(case when indiv.type = -10 then 1 else 0 end) as n_gone
            
        from bundestag_votings_individual indiv
        join bundestag_votings_meta meta
            on meta.id = indiv.id_meta
        join bundestag_members mems
            on mems.id = indiv.id_member
            
        where
            meta.term = 18

        group by mems.id_party, meta.id
    ) t
) s
    on s.id_party = indiv.id_party and s.id_meta = indiv.id_meta
join bundestag_members as mems
    on mems.id = indiv.id_member
join bundestag_parties as party
    on mems.id_party = party.id

where indiv.type <> -10 and mems.currently_active = TRUE

group by id_member, mems.name, party.name, party.code, mems.bundestag_profile_url
order by diff desc