# References

## To-Read
- [ ] Meade and Craig (2012)
- [ ] Insufficient effort responding: Examining an insidious confound in survey data.
- [ ] Kung et al. (2017): Are Attention Check Questions a Threat to Scale Validity?
- [ ] Breitsohl & Steidelmuller: The Impact of Insufficient Effort Responding Detection Methods on Substantive Responses: Results from an Experiment Testing Parameter Invariance
- [ ] The Differential Impacts of Two Forms of Insufficient Effort Responding (neat simulation study)
- [ ] Detecting Careless Responding in Survey Data Using Stochastic Gradient Boosting (useful for refs to mine)
- [ ] A little garbage in, lots of garbage out: Assessing the impact of careless responding in personality survey data (factor mixture model study)

## [Huang et al. (2012)](doi.org/10.1007/s10869-011-9231-8): Detecting and Deterring Insufficient Effort Responding to Surveys

In-person undergraduate sample for study of low-effort/inattentive responding. Advocate for use of (1) response time, (2) psychometric antonyms, and (3) individual reliability scores. Also suggests warning text about low-effort responding (e.g. "sophisticated statistical control methods"). Find evidence that removing low-effort respondents improves internal consistency and factor scores. Importantly, this paper provides evidence that  10%–20% of careless respondents in a sample are sufficient to render a single-factor confirmatory model incorrect.

## [Maniaci & Rogge (2014)](http://dx.doi.org/10.1016/j.jrp.2013.09.008): Caring about carelessness: Participant inattention and its effects on research

Really lovely paper

1. Evidence that inattentive responding reduces internal consistency
2. Evidence that inattentive responding suppresses correlations 
3. Removing can increase statistical power
4. Nice use of a simulation method

## [Huang et al. (2015)](https://doi.org/10.1007/s10869-014-9357-6): Detecting Insufficient Effort Responding with an Infrequency Scale: Evaluating Validity and Participant Reactions

Overview of the infrequency item approach.

## [Hauser & Schwarz (2016)](https://doi.org/10.3758/s13428-015-0578-z): Attentive Turkers: MTurk participants perform better on online attention checks than do subject pool participants

Find high rates of passing instructed items. Suggest this is a measure of quality. Do not discuss the possibility of random responding elsewhere.

Note 1: Good references for MTurk data quality and multi-tasking.

Note 2: Some good discussion on how reputation screening can actually self-select certain types of participants.

## [Thomas & Clifford (2017)](http://dx.doi.org/10.1016/j.chb.2017.08.038): Validity and Mechanical Turk: An assessment of exclusion methods and interactive experiments

Really excellent review of online study quality and methods to detect careless respondents. Similarly make the argument that the most common instructed items may not be particularly sensitive measures of attention, and that multiple screening methods should be used.

## [Buchanan & Scofield (2018)](https://doi.org/10.3758/s13428-018-1035-6) Methods to detect low quality data and its implication for psychological research

Directly references and addresses "automated form fillers" (e.g. "Form Filler" Google
Chrome plug-in). Suggest a number of metrics to collect for surveys: (1) page mouse clicks, (2) page timing. Form fillers on average have fewer page clicks. In an empirical study of over 1000 MTurkers, 2% were flagged with low click counts (~2 clicks), indicating auto-filling. Far more were flagged for fast page times (54%) and instructed questions (5%).

## [DeSimone & Harms (2018)](doi.org/10.1007/s10869-017-9514-9): Dirty Data: The Effects of Screening Respondents Who Provide Low-Quality Data in Survey Research

A small study of screening low-effort/inattentive responding on MTurk (N=307). Experiment comprised of two questionnaires (IPIP-VIA, 213 items; ACST, 24-items) for 1.00 pay (study time ~10 minutes). The authors tested a handful of screening metrics: (1) infrequency/instructed items; (2) response time (threhsold: 2s per item); (3) longstring analysis (threshold: 9 items), (4) individual response variability, or standard deviation of response; (5) psychometric synonyms (threshold: r=0.22), (6) personal reliability, or split-half reliability (threshold: r=0.30); and Mahalanobis D (threshold: top 5%).

There are three core results of interest to us:

1. In total, a high proportion of participants are flagged (75% of sample). Individual metrics have large variation in proportion of participanted flagged (mean: 20%, min: 5%, max: 40%).
2. The screening metrics are largely uncorrelated. Of the 233 individuals identified by screening techniques, almost half (115) were only identified by a single technique (77 were identified by two techniques). Thus, multiple screening techniques are warranted insofar that they may pick up on different forms of low-effort/inattentive responding. Some metrics show correlations where one would expect (e.g. psychometric synonyms and personal reliability are both intended to flag inconsistent responses, while longstring and IRV are both intended to flag invariant responses). Interestingly, invariant responders were more likely to miss infrequency items, suggesting that invariance strategies should be complimented by inconsistency strategies.
3. Screening out participants changes inter-item and inter-scale correlations. Importantly, some screening metrics (invariance metrics) may also reduce the internal consistency of unidimensional scales. As such, longstring should be used with caution.

## [Aruguete et al. (2019)](https://doi.org/10.1080/13645579.2018.1563966): How serious is the ‘carelessness’ problem on Mechanical Turk?

Use of consistency items in surveys flags more MTurkers than in-person respondents. Merely another method to point out. 

## [Barends & de Vries (2019)](http://dx.doi.org/10.1016/j.paid.2019.02.015): Noncompliant responding: Comparing exclusion criteria in MTurk personality research to improve data quality

Evidence that MTurk participants know to look for common infrequency/bogus/instructed items. Make the recommendation that multiple screening methods needed. Won't flag all individuals with just one item or one approach. 

## [Leiner (2019)](http://dx.doi.org/10.18148/srm/2019.v13i3.7403): Too Fast, too Straight, too Weird: Non-Reactive Indicators for Meaningless Data in Internet Surveys

Not much in the way of new insights, but study provides AUC analysis of several common screening methods. Also makes some helpful suggestions for detecting low-effort response patterns (straight-lining, zig-zagging).

## [Dennis et al. (2020)](https://doi.org/10.2308/bria-18-044): Online Worker Fraud and Evolving Threats to the Integrity of MTurk Data: A Discussion of Virtual Private Servers and the Limitations of IP-Based Screening Procedures

Example of the idea that online labor markets are always evolving. Need multitude of methods and constantly evolving practices. Some evidence of fraudulence. 
