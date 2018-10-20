**Goal**: The goal of this project is to build a forecasting model of regime backsliding and the closure of civic spaces.  US AID and our partner organizations want the ability to plan responses to regime backsliding and minimally warn people on the ground about the potential for negative regime actions.  To be useful, this tool must deal with events at the weekly or monthly level – if it is less granular than this, it won’t be a useful forecasting tool.  One issue is that most of the theoretical work about regime backsliding is not dynamic in nature, nor does it deal with high frequency data.

**Dependent variables**: We are most interested in three categories of behavior associated with civic spaces: the freedom of actors to associate, the freedom of speech, and the freedom from violence by the regime (either by imprisonment or physical harm).  We will thus run multiple forecasting models, each with a separate dependent variable (DV).  Challenges in measurement include attaining *high frequency data* on each of these categories (weekly or monthly) and dealing with the fact that different events have different magnitudes (e.g., jailing a group of journalists vs. turning off the internet for the entire country for a week).

**Independent variables**: The core independent variables (IV’s) will be event data.  Event data used in the IR literature codes events as (subject, target, action).  For our purposes, we aim to broaden the set of actions to focus on intrastate conflict and the closure of civic spaces, but we also aim to develop addition variables that capture the sentiment and topics latent in newsfeeds.  In addition, we also hope to ingest the text of executive orders, legislation, and court cases that bear on our target variables.  One challenge is that given we will be relying on latent variables in many cases, how will we interpret these variables / produce marginal effects such that aid organizations can derive actionable information from the model?

**Scope**: Initially, we will start with *Armenia, Kenya, Ukraine, Venezuela*.  Humans in the loop will gather information on the actors, actions, etc. (see below) for each case and will help us calibrate the models that will autonomously generate these data.  We will, however, broaden to the entire set of nations where US AID has interests.


# Classes of Actors

1. Chief executives
1. Supreme courts
1. Local courts
1. Electoral commissions
1. Police
1. Military
1. (Major) journalists
1. Media institutions
1. NGOs
1. Opposition politicans
1. Political/social activists

# Classes of actions:

**1. Violence/force:**   
  * Police violence against peaceful protesters
  * Police violence against members of opposition parties/civil society during demonstrations
  * Arrest/violence against journalists
  * Declare martial law
  * Violent outbreaks during elections

**2. Freedom of association & free speech:**    
  * Using defamation cases to silence any critics
  * Restrictive internet laws
  * Shutting down social media/internet/websites
  * Laws that restrict the right to assembly
  * Incarceration of opposition members
  * Changes to media ownership laws that limit competition or allow for consolidation
  * Limit size of groups that can gather in public/tighten regulations on public demonstrations
  * Imposing broadcast bans on media institutions about issues government do not like them being spread
  * Restricting party formation/competition

**3. Institutions:**    *EW: I don’t understand how some of these are “institutions”*
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
  * Not allowing International organizations to monitor elections
  * Increased number of corruption cases in the media
  * Non-punishment of the executive’s corrupt practices (EW: ?)
