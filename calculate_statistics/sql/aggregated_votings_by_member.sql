select
	party.name as party,
	party.code as party_code,
	mems.name as name,
	mems.bundestag_profile_url as profile_url,
	
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
	and mems.currently_active = TRUE

group by mems.name, party.name, mems.bundestag_profile_url, party.code
order by party, name asc