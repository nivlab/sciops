.. image:: https://img.shields.io/badge/python-3.6+-blue.svg
        :target: https://www.python.org/downloads/release/python-360/

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg
        :target: https://github.com/nivlab/sciops/blob/master/LICENSE

Spurious Correlations in Online Psychiatry Studies
==================================================

Code and data for Zorowitz, Solis, Niv, & Bennett (2023). *Inattentive responding can induce spurious associations between task behavior and symptom measures*. Nature Human Behaviour. `https://doi.org/10.1038/s41562-023-01640-7 <https://doi.org/10.1038/s41562-023-01640-7>`_

Project Organization
^^^^^^^^^^^^^^^^^^^^

The code for this project is divided across five branches:

::

    main (current branch)         <- all of the data and analysis code
    mturk-reversal-learning       <- software for the reversal learning experiment  (MTurk version)
    mturk-two-step                <- software for the two-step experiment           (MTurk version)
    prolific-reversal-learning    <- software for the reversal learning experiment  (Prolific version)
    prolific-two-step             <- software for the two-step experiment           (Prolific version)

The organization of the main branch (current branch) is as follows:

::

    ├── 01_Original               <- Notebooks, data, and code from the original study.
    ├── 02_Replication            <- Notebooks, data, and code from the replication study.
    ├── 03_Patients               <- Notebooks, data, and code from the patient study.
    ├── forums                    <- Examples of workers discussing attention checks.
    ├── manuscripts               <- LaTeX-formatted manuscripts.


Contact
^^^^^^^
Sam Zorowitz (zorowitz [at] princeton.edu)

Acknowledgements
^^^^^^^^^^^^^^^^
The research reported in this manuscript was supported in part by the National Institute of Mental Health (NIMH) under award number 5R01MH119511-02, and by the National Center for Advancing Translational Sciences (NCATS), a component of the National Institute of Health (NIH), under award number UL1TR003017. The content is  solely the responsibility of the authors and does not necessarily represent the official views of the National Institutes of Health. SZ was supported by an NSF Graduate Research Fellowship. DB was supported by an Early Career Fellowship from the Australian National Health and Medical Research Council (#1165010).
