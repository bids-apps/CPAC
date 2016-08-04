## C-PAC BIDS Application

The Configurable Pipeline for the Analysis of Connectomes [C-PAC](http://fcp-indi.github.io) is a software for performing high-throughput preprocessing and analysis of connectomes data using high-performance computers. This docker container, when built, is an application for performing participant and group level analyses.

### Documentation
Extensive information can be found in the [C-PAC User Guide](http://fcp-indi.github.com/docs/user/index.html).

### Reporting errors and getting help
Please report errors on the [C-PAC github page issue tracker](https://github.com/FCP-INDI/C-PAC/issues). Please use the [C-PAC google group](https://groups.google.com/forum/#!forum/cpax_forum) for help using C-PAC and this application.

### Acknowledgements
We currently have a publication in preparation, in the meantime please cite our poster from INCF:

    Craddock C, Sikka S, Cheung B, Khanuja R, Ghosh SS, Yan C, Li Q, Lurie D, Vogelstein J, Burns R, Colcombe S, Mennes M,
    Kelly C, Di Martino A, Castellanos FX and Milham M (2013). Towards Automated Analysis of Connectomes: The Configurable
    Pipeline for the Analysis of Connectomes (C-PAC). Front. Neuroinform. Conference Abstract: Neuroinformatics 2013.
    doi:10.3389/conf.fninf.2013.09.00042

    @ARTICLE{cpac2013,
        AUTHOR={Craddock, Cameron  and  Sikka, Sharad  and  Cheung, Brian  and  Khanuja, Ranjeet  and  Ghosh, Satrajit S  andYan, Chaogan  and  Li, Qingyang  and  Lurie, Daniel  and  Vogelstein, Joshua  and  Burns, Randal  and  Colcombe, Stanley  and  Mennes, Maarten  and  Kelly, Clare  and  Di Martino, Adriana  and  Castellanos, Francisco Xavier  and  Milham, Michael},  
        TITLE={Towards Automated Analysis of Connectomes: The Configurable Pipeline for the Analysis of Connectomes (C-PAC)},     
        JOURNAL={Frontiers in Neuroinformatics},
        YEAR={2013},
        NUMBER={42},
        URL={http://www.frontiersin.org/neuroinformatics/10.3389/conf.fninf.2013.09.00042/full},
        DOI={10.3389/conf.fninf.2013.09.00042},
        ISSN={1662-5196}
    }

### Usage
This App has the following command line arguments:

		usage: run.py [-h]
		              [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
		              bids_dir output_dir {participant,group}

		Example BIDS App entrypoint script.

		positional arguments:
		  bids_dir              The directory with the input dataset formatted
		                        according to the BIDS standard.
		  output_dir            The directory where the output files should be stored.
		                        If you are running group level analysis this folder
		                        should be prepopulated with the results of
		                        theparticipant level analysis.
		  {participant,group}   Level of the analysis that will be performed. Multiple
		                        participant level analyses can be run independently
		                        (in parallel).

		optional arguments:
		  -h, --help            show this help message and exit
		  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
		                        The label(s) of the participant(s) that should be
		                        analyzed. The label corresponds to
		                        sub-<participant_label> from the BIDS spec (so it does
		                        not include "sub-"). If this parameter is not provided
		                        all subjects should be analyzed. Multiple participants
		                        can be specified with a space separated list.
          --pipeline_file       Name for the pipeline configuration file to use, the path
                                must be accessible from inside the container.
                                default="/cpac_resources/default_pipeline.yaml"
          --n_cpus              Number of execution resources available for the pipeline
                                default="1"
          --mem                 Amount of RAM available to the pipeline in GB
                                default="6"
          --save_working_dir    Indicates that the working directory, which contains
                                intermediary files, should be saved. If specified, the
                                working directory will be saved in the output directory.

To run it in participant level mode (for one participant):

    docker run -i --rm \
		-v /Users/filo/data/ds005:/bids_dataset \
		-v /Users/filo/outputs:/outputs \
		bids/example \
		/bids_dataset /outputs participant --participant_label 01

After doing this for all subjects (potentially in parallel) the group level analysis
can be run:

    docker run -i --rm \
		-v /Users/filo/data/ds005:/bids_dataset \
		-v /Users/filo/outputs:/outputs \
		bids/example \
		/bids_dataset /outputs group
