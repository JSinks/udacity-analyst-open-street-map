# OpenStreetMap Data Project

## Map Area

[Marin County, CA, United States](https://www.openstreetmap.org/#map=12/38.0812/-122.7537)

This map is of the broader county that I currently reside in, so I was interested in what mapping data existed from the OMS project, and what trends (if any) some database queries would reveal.

## How to get started

1. Run `pip install -r requirements.txt` to install required python packages (necessary for loading data)
1. Run `python db_setup.py` to create the appropriate sqlitedb and table schema
2. Run `python load_data.py <map name>` to cleanse the data, create csvs, and refresh the DB

## Problems Encountered

After downloading the data, I began to explore the information that was provided and came across a number of issues. The problems that I ran into are discussed in order below:

1. Enhancement to the lower colon RE to help split keys
1. Fixme data keys?
1. Multiple key names related to the same data point
1. Tags with multiple colons in key


### Lower colon RE fixes
The original RE for parsing out keys that contained a colon would only successfully parse a key that had lower case characters preceeding the colon, and lower case characters (or _'s) following the colon.

However it turned out that there were a number of keys that had caps before or after the colons, as well as numbers after the colon.

To better represent the data, I updated the regular expression to take these differences into account.
However that led to the next challenge...


### Tags with multiple colons

After applying this fix, I then found that there were some keys that contained more than one colon.
Unfortunately in this case it was not possible to suppose what combination would be considered correct to split.

e.g. destination:ref:backward OR destination:ref:lanes:backward

These were left in place without additional modification. I decided they would not be critical for my analysis regardless.


### Lots of keys

Even after these reductions I was still left with hundreds of unique keys which makes parsing and finding data that is of interest very difficult. Further analysis could be done to reduce and better group some of these keys which would make ongoing analysis more painless.





## Data Overview

This section contains some basic queries to investigate the data as provided, the SQL queries to gather the desired data, and some ideas for futher analysis that could be performed about the data.

### File Sizes

```
marin-county-map.xml ........ 87.3 MB
osm-data.db ................. 45.0 MB
nodes.csv ................... 33.2 MB
nodes_tags.csv ..............  1.2 MB
ways.csv ....................  2.1 MB
ways_tags.csv ...............  5.2 MB
ways_nodes.csv ..............  9.9 MB
```

### Number of nodes
```
select count(*) 
from nodes;
```
```
398856
```


### Number of ways
```
select count(*) 
from nodes;
```
```
35003
```

### Number of unique users contributing
The count of users who have contributed any number of nodes
```
with all_contributors as (
  select uid, user
  from nodes
  union all
  select uid, user
  from ways
)
select count(distinct uid)
from all_contributors;
```
```
769
```

### Top 10 contributors
```
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
```

| Name | Contributions |
|:------|------:|
| GITNE | 35055 |
| Gone | 22428 |
| paulmach | 18882 |
| dchiles | 17591 |
| woodpeck_fixbot | 17402 |
| wvdp | 14763 |
| nmixter | 14685 |
| Apo42 | 12488 |
| bhavana naga| 12128 |
| Chris Lawrence| 10792 |


### Number of users with 3 of less contributions
```
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
```
```
211
```


## Additional Analysis
### Top 10 types of amenities
```
select value, count(*) 
from ways_tags 
where key = 'amenity' 
group by 1 
order by 2 desc 
limit 10;
```

| Type of Amenity | Number in Area |
|:----|-----:|
parking|661
restaurant|256
school|194
bench|172
toilets|119
drinking_water|76
place_of_worship|75
cafe|72
fuel|58
bank|56

The number of parking amenities in the area seems abnormally high, let's dig into that a little further and see if there is anything more we can identify.

Analysing other tags that are applied to these parking amenities with the following query:
```
with parking_tags as (
    select id 
    from ways_tags 
    where key = 'amenity' 
    and value = 'parking'
) 
select * 
from ways_tags 
where id in (select id from parking_tags) 
order by 1;
```

Interestingly this does not show anything particularly weird about what has been turned up.
The parking amenity seems to get associated with individual parking spaces, and there just happen to be a lot in the area.

### Favourite types of restaurants
Finally I wanted to see what the cuisines were offered at restaurants in the area and if a particular one was most common.

```
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
```

| Cuisine | # of restaurants |
|:----|----:|
mexican|25
italian|19
american|18
pizza|18
seafood|12
chinese|10
thai|9
sandwich|8
burger|7
regional|7
french|6
indian|6
sushi|5
japanese|3
asian|2
sushi;japanese|2
American_/_Mexican|1
Himalayan|1
american;breakfast;lunch|1
bagels;sandwiches;jewish|1
beer;american|1
breakfast|1
burger; seafood|1
burger;ice_cream|1
burger;korean|1
coffee_shop|1
deli|1
farm-to-table|1
fish_and_chips|1
hawaiian|1
ice_cream|1
indian;vegetarian|1
italian_pizza|1
mexican;pizza;sandwich|1
pizza,_burger,_beer,_woodoven,_brewery|1
pizza;italian|1
portuguese|1
puerto_rican|1
sandwich;asian|1
thai;chinese|1
vietnamese|1

Mexican restaurants topping the list does not surprise me based on my own experience dining in Marin.

## Conclusion

The analysis of the marin county data has left me with a few conclusions. First the data is relatively clean, there were not a significant amount of errors encountered when importing the data. The number of contributors to the marin county map area is relatively low, with a small number of contributors doing most of the work (82% of contributions are from the top 50 contributors).

I think there is an opportunity to enrich the quality of the OSM data by making the mapping data more accessible and easier to contribute to for the general public. Providing an application on top of OSM that allows locals to add information about stores, road work, etc could allow more real-time contribution by a greater number of non-technical users.

This would require some engineering effort (potentially in the form of a simple mobile application), but would allow for non-engineers to more readily contribute to the project and overall enhancing the quality of the data available.


## References

I referenced the following articles while completing this project:

* https://gist.github.com/swwelch/f1144229848b407e0a5d13fcb7fbbd6f
* https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md
* https://stackoverflow.com/questions/14108162/python-sqlite3-insert-into-table-valuedictionary-goes-here
* https://wiki.openstreetmap.org/wiki/Elements
* https://stackoverflow.com/questions/3086973/how-do-i-convert-this-list-of-dictionaries-to-a-csv-file
* https://stackoverflow.com/questions/5838605/python-dictwriter-writing-utf-8-encoded-csv-files/5838817
* https://www.tablesgenerator.com/markdown_tables