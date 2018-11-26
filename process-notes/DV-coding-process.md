# Rules for coding initial DV

## Media Sources

## Sample data

### JSON (native)

<details><summary>Expand</summary>
<p>

```javascript
{
	"event_id":"000001",
	"date:":"2018-07-01",
	"event_type":"arrest",
	"district":"",
	"city":"",
	"gadm_1":"",
	"informal_region":"",
	"country":"",
	"subject":
			{
				"type":"police",
				"level":"federal",
				"organization_name":"SBU",
				"individual_name":"",
				"id":"555555"
			},
	"targets": [
				{
					"type":"journalist",
					"organization_name":"freelance",
					"individual_name":"Antonio Pampliega",
					"nationality":"ESP",
					"id":"555556",
					"count":"1"
				},
				{
					"type":"journalist",
					"organization_name":"freelance",
					"individual_name":"Ángel Sastre",
					"nationality":"ESP",
					"id":"555557",
					"count":"1"
				}
				],
	"sources": [
				{
					"link": "https://cpj.org/2017/08/ukraine-bars-spanish-journalists-over-coverage-of-.php",
					"text": "The Security Service of Ukraine today said that it barred the Spanish freelance journalists Antonio Pampliega and Ángel Sastre from entering the country for three years over their reporting on the conflict in the east, according to news reports…."},
				{
					"link": "https://www.ukrinform.net/rubric-crime/2294816-two-spanish-journalists-banned-from-entering-ukraine-until-2020-due-to-antiukrainian-activities-sbu.html",
					"text": "The Security Service of Ukraine (SBU) bans the entry into Ukraine to Spanish journalists Antonio Pampliega and Manuel Angel Sastre due to their anti-Ukrainian activities…"}
				]
}
```
</p>
</details>

### Table

<details><summary>Expand</summary>
<p>

| event_id | date       | event_type | subject_type | subject_level | subject_organization_name | subject_individual_name | subject_id | target_type | target_individual_name | target_nationality | target_id | target_organization_name | target_count | district | city | level_1_administrative_region | informal_region | country | source_0                                                                       | text_0                           | source_1                                                                                                                                                | text_1                            |
|----------|------------|------------|--------------|---------------|---------------------------|-------------------------|------------|-------------|------------------------|--------------------|-----------|--------------------------|--------------|----------|------|-------------------------------|-----------------|---------|--------------------------------------------------------------------------------|----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| 1        | 2017-08-29 | deport     | police       | federal       | SBU                       |                         | 555555     | journalist  | Antonio Pampliega      | ESP                | 555556    | freelance                | 1            |          | Kiev | Kiev                          |                 | Ukraine | https://cpj.org/2017/08/ukraine-bars-spanish-journalists-over-coverage-of-.php | The Security Service of Ukraine… | https://www.ukrinform.net/rubric-crime/2294816-two-spanish-journalists-banned-from-entering-ukraine-until-2020-due-to-antiukrainian-activities-sbu.html | The Security Service of Ukraine … |
| 1        | 2017-08-29 | deport     | police       | federal       | SBU                       |                         | 555555     | journalist  | Ángel Sastre           | ESP                | 555557    | freelance                | 1            |          | Kiev | Kiev                          |                 | Ukraine | https://cpj.org/2017/08/ukraine-bars-spanish-journalists-over-coverage-of-.php | The Security Service of Ukraine… | https://www.ukrinform.net/rubric-crime/2294816-two-spanish-journalists-banned-from-entering-ukraine-until-2020-due-to-antiukrainian-activities-sbu.html | The Security Service of Ukraine … |

</p>
</details>


## Columns

### event_id
  Unique id number for each event. Useful events with multiple targets. One row for each named target, can easily collapse to single row via event_id

### date
  Event date

### event_type
  The "verb" in the event. 
  
  1. 
  1. 
  1. 
  1. 

### subject_type
  
