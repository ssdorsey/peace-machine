# Rules for coding initial DV
The present document outlines the main components of the coding procedure. It defines the way we are identifying the sources of information as well as the specifications of some of the information we want to capture from each source. Moving forward we are missing a detailed list of keywords for each one of our dependent variables that would be used to scrape the news in the future. This list will be in English but, will also contain translations in the local languages of our first 4 targeted countries. Finally, the idea is that after the initial test we are running, we will scrape the news from the media sources identified and give them to the new coders. This means, that all the news inputs will be done by out scraping exercise but coded manually. This decreases the subjectivity in the search terms and helps have a more consistent/comparable approach to teh data. 

## Media Sources

### Local
1. To start with, we will scrape the top-5 most-popular news websites (according to Alexa) for each country. This way, we can "objectively" determine which ones are the most important papers in terms of views. Instead of relying on other algorithms like the one used by Google News.   
2. We will also build a comprehensive list of digitially-available local media for later download + machine coding 
   * Wikipedia already has very good lists available
   * The idea is to capture local media here that could give more reports on some of the activities we are interested. Our concern here is just that increasing the number of sources we can include a lot of noise into our data. 

### International
1. BBC
1. NYT
1. AP
1. AFP
1. **Other major papers, wires, and specialty publications like Devex**

## Initial filtering

1. For each event type will build logical search phrases that will capture every possibly-relevant news story
1. Restrict based on time for intial test (ex: 2015-2017)
1. Event creation
  1. Using the restricted corpus, hand-coders will create events using a platform like dataturks
  1. Computer will do the same
1. Evaluate

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

**We need to get more specific coding rules but let's check to see if we have everything we want here first**

### event_id
Unique id number for each event. Useful events with multiple targets. One row for each named target, can easily collapse to single row via event_id

### date

  Event date

### event_type

  The "verb" in the event. Targets of interest under each. 
  
  **We will likely need more sub-categories under each of these**
  
1. Non-lethal violence
   * protesters
   * journalists
   * activists
   * political opposition
1. Lethal violence
   * protesters
   * journalists
   * activists
   * political opposition
1. Arrest
   * protesters
   * journalists
   * activists
   * political opposition
1. Restrict speech rights
1. Restrict assembly rights
1. Restrict freedom movement
1. Restrict religious freedom
1. Restrict association
   * political opposition
   * labor
1. Politically-motivated defamation suit
1. Politically-motivated regulatory hurdles
   * NGO
   * aid organization
1. Shut down
   * media organization 
   * political group
1. Ban access
   * website


  

### district

Named district within city (for large events across multiple districts only include city)

### city

### gadm_1

GADM administrative level1. Equivalent of US state

### informal region

Use this only if no other location information is available. ex: "Protests in central Ukraine turned violent..."

### country

ISO-3. ex: Ukraine = UKR

### subject_type

The "doer". For civic closures this will generally be a government actor. We anticipate that this list will include many other actors once IVs are coded. 

Only the individual or body whose actions or orders change the status quo should be assigned as the subject. For example, assume a legislature passes a bill closing civic spaces but the bill requires the Executive's signature before going into effect. There is no civic closure until the Executive signs the bill and _only_ the executive will be listed as the subject.
  
1. Police
1. Military
1. Legislature 
1. Judiciary 
1. Executive
1. Intelligence organization
1. Regulatory agency
1. Suspected government affiliate
   * for cases where it is widely understood that government agents are the subject but no clear responsibility is assigned
1. Non-state
   * for cases where pseudo-governmental organizations like drug cartels or rebel groups close civic spaces
	
### subject_adm_level 

For distinguishing between local, regional, and federal actors. For example, a Governor would have subject_type "Executive" and subject_adm_level "1"

0: Federal
1: Equivalent to US state
2: city/local 

### subject_organization_name

Name of subject's organization name. EX: Ukraine's SBU

### subject_individual_name

Individual name of subject (if applicable)

### subject_individual_id

For mapping to actor dictionary

### target_type

Civic classification of target

1. Politician
1. Political party
1. Activist
1. Labor organization
1. Journalist (and affiliates like photographers)
1. Media organization
1. Website
1. NGO / Aid organization
1. Business leader
1. Ethnic/religious group
1. Protester
1. General populace
   * for when broad laws or reforms are enacted. ex: martial law


### target_individual_name

When a target's individual identity is important. ex: politician, notable business leader, activist. Not required when population or specific organizations are targets. 

### target_organization_name

Only name if the organization is the target, umbrella organization for individuals. ex: Newspaper that employs targeted journalist.

### target_id

For mapping to actor dictionary

### source_link

Link to text source

### source_text
 
Captured text (never distribute!)
