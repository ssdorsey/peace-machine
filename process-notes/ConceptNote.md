# Machine Learning for Peace

## Overview 

**Goal**: The goal of this project is to build a forecasting model of civic-space closures. Roughly defined, a closure of a civic space occurs whenever a government significantly and negatively impacts its citizens' freedom of speech or freedom of association. US AID and our partner organizations want the ability to plan responses to these closures and minimally warn people on the ground about their potential. To be useful, this tool must deal with events at the *weekly or monthly* level – if it is less granular than this, it won’t be a useful forecasting tool. One issue is that most of the theoretical work in this area is not dynamic, nor does it deal with high-frequency data.  

To build models that can keep up with rapidly-changing events, we will rely on a mix of algorithmically-generated data from traditional media sources, social media, and NGO reports. Using this approach, we will create a historical dataset of civic-space closures to train on our models on and a near-real-time pipeline for processing new data and producing predictions. We will also track interventions by our partner organizations to see if they have any effect on the likelihood of civic space closures.

**Dependent variables**: We are most interested in three categories of behavior associated with civic spaces: the freedom of actors to associate, the freedom of speech, and the freedom from violence by the regime (either by imprisonment or physical harm).  While the behaviors we are trying to predict are thematically linked, the conditions that would lead a potentially-oppressive regime to shut down the Internet are separate enough from the conditions that would cause them to ban an opposition political party that we will be required to build bespoke models for each. While we are agnostic about specific methodological approaches, we will aim to maximize predictive capacity while maintaining a minimum standard of interpretability that will allow us to make recommendations about possible interventions. Challenges in measurement include attaining *high frequency data* on each of these categories (weekly or monthly) and dealing with the fact that different events have different magnitudes (e.g., jailing a group of journalists vs. turning off the internet for the entire country for a week).

**Independent variables**: The core independent variables (IV’s) will be event data.  Event data used in the IR literature codes events as (subject, target, action).  For our purposes, we aim to broaden the set of actions to focus on intrastate conflict and the closure of civic spaces, but we also aim to develop additional variables that capture the sentiment and topics latent in newsfeeds.  In addition, we also hope to ingest the text of executive orders, legislation, and court cases that bear on our target variables.  One challenge is that given we will be relying on latent variables in many cases, how will we interpret these variables / produce marginal effects such that aid organizations can derive actionable information from the model?

**Scope**: Initially, we will start with *Armenia, Kenya, Ukraine, Venezuela*.  Humans in the loop will gather information on the actors, actions, etc. (see below) for each case and will help us calibrate the models that will autonomously generate these data.  We will, however, broaden to the entire set of nations where US AID has interests.

## Responses
After our first approximation to the literature related to the closure of civic space as well as a detailed analysis of certain cases, we identified a series of specific events that could be used to model our dependent variable. As exposed previously, most of the literature focus on non-frequent events that affect the legal-framework of a country. However, we consider those as independent variables that would lead to changes in the frequencies of the events we are trying to model. A first list of events we will model is as follows:

### Freedom of speech
* Internet shutdowns
* Blocking websites that would not be banned in a free society (i.e. blocking Instagram or YouTube)

* Arrest/violence against journalists
* Closure/limiting distribution of media organization or coverage
* Serkant: Discriminating against opposition media organizations in state ads, in press conferences etc.
* Serkant: Imposing broadcast bans on various issues that government sees as sensitive

* Charging individuals with blasphemy 
* Passing new laws that ban the criticism of government or religion 


### Mix
* Police violence against peaceful protesters / ordinary citizens

* Declare martial law


### Freedom of association
* Incarceration or assassination of political opposition
* Banning political opposition party(ies) or barring specific opposition members from seeking office
* Damage electoral integrity

* Limit size of groups that can gather in public

* Serkant: Laws that bring de facto obstacles to gathering (e.g., designing special meeting places and banning any other meeting outside these places)
* Banning associations amongst civil society's groups or between them and international actors
* Expulsion of NGOs working on the country

## Possible features
An early list features we hope to use in the models

* Topics and sentiments of local media stories
* Topics and sentiments of relevant international media stories
* Topics and sentiments of social media posts
* Strength of institutional protection for civic spaces
* Changes in institutional protection for civic spaces
* Economic shocks
* Increase in speech targeting minority groups
* Increase in corruption cases reported in media
* Increase in protests

...

