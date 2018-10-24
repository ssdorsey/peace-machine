# Machine Learning for Peace

## Overview

**Goal**: The goal of this project is to build a forecasting model of civic-space closures. Roughly defined, a closure of a civic space occurs whenever a government significantly and negatively impacts its citizens' freedom of speech or freedom of association. Closures of civic spaces are conceptually related to, but distinct from, democratic breakdowns; we think of the latter as primarily institutional, while the former involve the output of institutions. USAID and our partner organizations want the ability to plan responses to these closures and minimally warn people on the ground about their potential. To be useful, this tool must deal with events at the *weekly or monthly* level – if it is less granular than this, it will not be a useful forecasting tool. One issue is that most of the theoretical work in this area is not dynamic, nor does it deal with high-frequency data.  

To build models that can keep up with rapidly-changing events, we will rely on a mix of algorithmically-generated data from traditional media sources, social media, speeches and NGO reports. Using this approach, we will create a historical dataset of civic-space closures to train on our models plus a near-real-time pipeline for processing new data and producing predictions. We will also engage in careful design, monitoring and evaluation of the interventions by our partner organizations to see if they have any effect on civic space closures; monitoring and evaluation data from these field projects will likely be fed into the larger forecasting effort.

**Dependent variables**: We are most interested in three categories of behavior associated with civic spaces: the freedom of actors to associate, the freedom of speech, and freedom from violence by the regime (either by imprisonment or physical harm).  While the behaviors we are trying to predict are thematically linked, the conditions that would lead a potentially-oppressive regime to shut down the Internet are separate enough from the conditions that would cause them to ban an opposition political party that we will need to build bespoke models for each. While we are agnostic about specific methodological approaches, we will aim to maximize predictive capacity while maintaining a minimum standard of interpretability that will allow us to make recommendations about possible interventions. Challenges in measurement include attaining *high frequency data* on each of these categories (weekly or monthly) and dealing with the fact that different events have different magnitudes (e.g., jailing a group of journalists vs. turning off the internet for the entire country for a week).

**Independent variables**: The core independent variables (IV’s) will be event data.  Event data used in the IR literature codes events as (subject, target, action).  For our purposes, we aim to broaden the set of actions to focus on intrastate conflict and the closure of civic spaces, but we also aim to develop additional variables that capture the sentiment and topics latent in newsfeeds.  In addition, we also hope to ingest the text of executive orders, presidential speeches, legislation, and court cases that bear on our target variables.  One challenge is that we will be relying on latent variables in many cases; given that, how will we interpret these variables / produce marginal effects such that aid organizations can derive actionable information from the model?

**Scope**: Initially, we will start with *Armenia, Kenya, Ukraine, Venezuela*.  Humans in the loop will gather information on the actors, actions, etc. (see below) for each case and will help us calibrate the models that will autonomously generate these data.  We will, however, broaden to the entire set of nations where USAID has interests.

## Targets
After our first approximation to the literature on closures of civic space, as well as a detailed analysis of certain cases, we identified a series of specific events that could be used to model our dependent variables. Previously, most of the literature focused on rare events that affect the legal-framework of a country -- for instance, packing high courts or extending/eliminating term limits on the chief executive. However, we consider those as independent variables that would lead to changes in the frequencies of the events we are trying to model. A first list of events we will model is as follows:

 ### Dependent variables/classes of actions:

 **1. Violence/force:**   
   * Police violence against peaceful protesters
   * Police violence against members of opposition parties/civil society during demonstrations
   * Arrest/violence against journalists
   * Declaration of martial law
   * Violent outbreaks during elections

 **2. Freedom of association & free speech:**    
   * Using defamation cases to silence critics
   * Restrictive internet laws
   * Shutting down social media/internet/websites
   * Laws that restrict the right to assembly
   * Laws that restrict the formation and/or operation of non-governmental organizations, civil society organizations
   * Incarceration of opposition members
   * Changes to media ownership laws that limit competition or allow for consolidation
   * Limit size of groups that can gather in public/tighten regulations on public demonstrations
   * Imposing broadcast bans on media institutions about certain issues (which issues?)
   * Restricting party formation/competition

 ### Independent variables

 **1. Institutional warning signs:**    
   * Packing local courts
   * Packing higher courts such as Supreme Court, State Council, and High Council of Judges and Prosecutors
   * Packing the military or the police forces
   * New laws regulating civil service
   * New laws giving the executive nomination powers
   * Erosion of the autonomy/authority of the electoral commission or electoral authorities.
   * Purging members of the ruling party
   * Extending or eliminating terms limits of chief executive
   * Calling irregular elections or constitutional referenda
   * Rescheduling/Postponing/Cancelling regularly-scheduled elections
   * Appointment of the President’s family members in governmental institutions
   * Changing rules for political competition (i.e. requirements for parties)
   * Increased reliance on executive orders

 **4. Internal/External Threats:**   
   * Declarations of strident nationalism, anti-foreign, anti-U.S., etc.
   * Sudden emphasis on national security/sovereignty concerns
   * Demonization of national/ethnic/religious minorities
   * Demonization of the opposition
   * Anti-“elite” language

 **5. Others:**    *EW: these below seem too vague to be actionable*
   * Polarization of civil society
   * Increase in demands to international organizations
   * Not allowing international organizations to monitor elections
   * Increased number of corruption cases in the media

### Classes of Actors
Note that we will be building a dictionary with the proper names of these actors.

  * Chief executives
  * Supreme courts
  * Local courts
  * Electoral commissions
  * Police
  * Military
  * (Major) journalists
  * Media institutions
  * NGOs
  * Opposition politicans
  * Political/social activists

We have several questions for workshop participants. In pondering them, please keep in mind the very particular nature of the data we are dealing with (i.e. high frequency event data):
  1. Do we have the right set of outcome variables? Are there other important examples of civic space closures we are missing?
  2. Do we have the right independent variables? What other behaviors or statements do governments engage in that might help forecast crackdowns on civic space? Note that we can think of this in terms of "causes" or as events/actions/statements that are associated with, but temporally antecedent to, closures of civic spaces.
  3. Are we missing any crucial actors?
