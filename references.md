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

## [Huang et al. (2015)](https://doi.org/10.1007/s10869-014-9357-6): Detecting Insufficient Effort Responding with an Infrequency Scale: Evaluating Validity and Participant Reactions

Overview of the infrequency item approach.

## [Buchanan & Scofield (2018)](https://doi.org/10.3758/s13428-018-1035-6) Methods to detect low quality data and its implication for psychological research

Directly references and addresses "automated form fillers" (e.g. "Form Filler" Google
Chrome plug-in). Suggest a number of metrics to collect for surveys: (1) page mouse clicks, (2) page timing. Form fillers on average have fewer page clicks. In an empirical study of over 1000 MTurkers, 2% were flagged with low click counts (~2 clicks), indicating auto-filling. Far more were flagged for fast page times (54%) and instructed questions (5%).

## [DeSimone & Harms (2018)](doi.org/10.1007/s10869-017-9514-9): Dirty Data: The Effects of Screening Respondents Who Provide Low-Quality Data in Survey Research

A small study of screening low-effort/inattentive responding on MTurk (N=307). Experiment comprised of two questionnaires (IPIP-VIA, 213 items; ACST, 24-items) for 1.00 pay (study time ~10 minutes). The authors tested a handful of screening metrics: (1) infrequency/instructed items; (2) response time (threhsold: 2s per item); (3) longstring analysis (threshold: 9 items), (4) individual response variability, or standard deviation of response; (5) psychometric synonyms (threshold: r=0.22), (6) personal reliability, or split-half reliability (threshold: r=0.30); and Mahalanobis D (threshold: top 5%).

There are three core results of interest to us:

1. In total, a high proportion of participants are flagged (75% of sample). Individual metrics have large variation in proportion of participanted flagged (mean: 20%, min: 5%, max: 40%).
2. The screening metrics are largely uncorrelated. Of the 233 individuals identified by screening techniques, almost half (115) were only identified by a single technique (77 were identified by two techniques). Thus, multiple screening techniques are warranted insofar that they may pick up on different forms of low-effort/inattentive responding. Some metrics show correlations where one would expect (e.g. psychometric synonyms and personal reliability are both intended to flag inconsistent responses, while longstring and IRV are both intended to flag invariant responses). Interestingly, invariant responders were more likely to miss infrequency items, suggesting that invariance strategies should be complimented by inconsistency strategies.
3. Screening out participants changes inter-item and inter-scale correlations. Importantly, some screening metrics (invariance metrics) may also reduce the internal consistency of unidimensional scales. As such, longstring should be used with caution.

## [Barends & de Vries (2019)](http://dx.doi.org/10.1016/j.paid.2019.02.015): Noncompliant responding: Comparing exclusion criteria in MTurk personality research to improve data quality

Evidence that MTurk participants know to look for common infrequency/bogus/instructed items.

## [Leiner (2019)](http://dx.doi.org/10.18148/srm/2019.v13i3.7403): Too Fast, too Straight, too Weird: Non-Reactive Indicators for Meaningless Data in Internet Surveys

Not much in the way of new insights, but study provides AUC analysis of several common screening methods. Also makes some helpful suggestions for detecting low-effort response patterns (straight-lining, zig-zagging).
