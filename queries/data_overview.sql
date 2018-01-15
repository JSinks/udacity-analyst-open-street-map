select count(*) from nodes;
--398856

select count(*) from ways;
--35003

with all_contributors as (
  select uid, user
  from nodes
  union all
  select uid, user
  from ways
)
select count(distinct uid)
from all_contributors;
-- 769

with all_contributors as (
  select uid, user
  from nodes
  union all
  select uid, user
  from ways
),
contributor_names as (
  select distinct uid, user
  from all_contributors
),
top_10_contributors as (
  select uid, count(*) as num_contributions
  from all_contributors
  group by 1
  order by 2 DESC
  limit 10
)
select user, num_contributions
from top_10_contributors target
join contributor_names name on target.uid = name.uid
order by 2 desc;
/*
GITNE|35055
Gone|22428
paulmach|18882
dchiles|17591
woodpeck_fixbot|17402
wvdp|14763
nmixter|14685
Apo42|12488
bhavana naga|12128
Chris Lawrence|10792
*/

with all_contributors as (
  select uid, user
  from nodes
  union all
  select uid, user
  from ways
),
less_than_4_contributions as (
  select uid, count(*) as num_contributions
  from all_contributors
  group by 1
  having count(*) <= 3
)
select count(uid) as num_of_low_contributors
from less_than_4_contributions;

with all_contributors as (
  select uid, user
  from nodes
  union all
  select uid, user
  from ways
),
contributions_per_user as (
  select uid, count(*) as num_contributions
  from all_contributors
  group by 1
)
select num_contributions, count(uid) as num_of_users
from contributions_per_user
group by 1
order by 1;
-- Distribution of contributions (histogram)

with all_contributors as (
  select uid, user
  from nodes
  union all
  select uid, user
  from ways
),
target_contributors as (
  select uid, count(*) as num_contributions
  from all_contributors
  group by 1
  order by 2 DESC
  limit 10
)
select sum(num_contributions) * 1.0 / (398856 + 35003) * 1.0
from target_contributors;
-- contribution of the top 10 users
-- 40.61%

with all_contributors as (
  select uid, user
  from nodes
  union all
  select uid, user
  from ways
),
target_contributors as (
  select uid, count(*) as num_contributions
  from all_contributors
  group by 1
  order by 2 DESC
  limit 1
)
select sum(num_contributions) * 1.0 / (398856 + 35003) * 1.0
from target_contributors;
-- contribution of the top user
-- 8.08%

with all_contributors as (
  select uid, user
  from nodes
  union all
  select uid, user
  from ways
),
target_contributors as (
  select uid, count(*) as num_contributions
  from all_contributors
  group by 1
  order by 2 DESC
  limit 50
)
select sum(num_contributions) * 1.0 / (398856 + 35003) * 1.0
from target_contributors;
-- contribution of the top 50 users
-- 82.06%

with all_tags as (
  select key, value
  from ways_tags
  union all
  select key, value
  from nodes_tags
)
select value, count(*)
from all_tags
where key = 'amenity'
group by 1
order by 2 desc
limit 10;


with all_tags as (
  select id, key, value
  from ways_tags
  union all
  select id, key, value
  from nodes_tags
),
restaurant_tags as (
  select id
  from ways_tags
  where key = 'amenity'
  and value = 'restaurant'
  union all
  select id
  from nodes_tags
  where key = 'amenity'
  and value = 'restaurant'
)
select value, count(*)
from all_tags
where id in (select id from restaurant_tags)
and key = 'cuisine'
group by 1
order by 2 desc;