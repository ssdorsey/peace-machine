# Machine Learning for Peace

## Overview 

The goal of this project is to build a forecasting model of civic-space closures. Roughly defined, a closure of a civic space occurs whenever a government significantly and negatively impacts its citizens' freedom of speech or freedom of association. US AID and our partner organizations want the ability to plan responses to these closures and minimally warn people on the ground about their potential. To be useful, this tool must deal with events at the weekly or monthly level – if it is less granular than this, it won’t be a useful forecasting tool. One issue is that most of the theoretical work in this area is not dynamic, nor does it deal with high-frequency data.

To build models that can keep up with rapidly-changing events, we will rely on a mix of algorithmically-generated data from traditional media sources, social media, and NGO reports. Using this approach, we will create a historical dataset of civic-space closures to train on our models on and a near-real-time pipeline for processing new data and producing predictions. 

While the behaviors we are trying to predict are thematically linked, the conditions that would lead a potentially-oppressive regime to--for example--shutdown the Internet are separate enough from the conditions that would cause them to ban an opposition political party that we will be required to build bespoke models for each. While we agnostic about specific methodological approaches, we will aim to maximize predictive capacity while maintaining a minimum standard of interpretability that will allow us to make recommendations about possible interventions. 

## Responses

### Freedom of speech
* Internet shutdowns
* Blocking websites that would not be banned in a free society (i.e. blocking Instagram)

* Charging individuals with blasphemy 
* Passing new laws that ban the criticism of government or religion 


### Mix
* Police violence against peaceful protesters 

* Arrest/violence against journalists
* Declare martial law


### Freedom of association
* Incarceration or assassination of political opposition
* Banning political opposition party(ies) or barring specific opposition members from seeking office
* Damage electoral integrity

* 


#### General features
