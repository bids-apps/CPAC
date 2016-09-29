import os
import yaml

def gen_bids_sublist(paths_list):

    subdict = {}

    for p in paths_list:
        p = p.rstrip()
        f=os.path.basename(p)
        if f.endswith(".nii") or f.endswith(".nii.gz"):
            f_dict={}
            for key_val_pair in f.split("_"):
                key_val_pair=key_val_pair.lower()
                if not "nii" in key_val_pair:
                    chunks = key_val_pair.split("-")
                    f_dict[chunks[0]] = "-".join(chunks[1:])
                else:
                    f_dict["scantype"] = key_val_pair.split(".")[0]

            if "ses" not in f_dict:
                f_dict["ses"] = "1"

            if f_dict["sub"] not in subdict:
                subdict[f_dict["sub"]] = {}

            if f_dict["ses"] not in subdict[f_dict["sub"]]:
                subdict[f_dict["sub"]][f_dict["ses"]]=\
                {"subject_id":"-".join(["sub",f_dict["sub"]]),\
                 "unique_id":"-".join(["ses",f_dict["ses"]])}

            if "t1w" in f_dict["scantype"]:
                if not "anat" in subdict[f_dict["sub"]][f_dict["ses"]]:
                    subdict[f_dict["sub"]][f_dict["ses"]]["anat"]=p
                else:
                    print "Anatomical file (%s) already found for (%s:%s)"+\
                        " discarding %s"%(\
                        subdict[f_dict["sub"]][f_dict["ses"]]["anat"],
                        f_dict["sub"],
                        f_dict["ses"],
                        p)

            if "bold" in f_dict["scantype"]:
                task_key = "-".join(["task",f_dict["task"]])
                if "acq" in f_dict:
                    task_key = "_".join([task_key,\
                        "-".join(["acq",f_dict["acq"]])])
                if not "rest" in subdict[f_dict["sub"]][f_dict["ses"]]:
                    subdict[f_dict["sub"]][f_dict["ses"]]["rest"]=\
                        {task_key:p}
                elif not task_key in \
                    subdict[f_dict["sub"]][f_dict["ses"]]["rest"]:
                    subdict[f_dict["sub"]][f_dict["ses"]]["rest"][task_key]=p
                else:
                    print "Func file (%s) already found for (%s:%s:%s)"+\
                        " discarding %s"%(\
                        subdict[f_dict["sub"]][f_dict["ses"]]["rest"][task_key],
                        f_dict["sub"],
                        f_dict["ses"],
                        task_key,
                        p)

    sublist = []
    for sub in subdict.itervalues():
        for ses in sub.itervalues():
            if "anat" in ses and "rest" in ses:
                sublist.append(ses)
            else:
                print "No anat or rest found for %s %s"%(ses["subject_id"],
                    ses["unique_id"])
    
    return sublist

def test_gen_bids_sublist(paths_file,test_yml):

    paths_list=[]
    with open(paths_file, "r") as fd:
        paths_list=fd.readlines()

    print len(paths_list)
    sublist=gen_bids_sublist(paths_list)

    with open(test_yml,"w") as ofd:
        yaml.dump(sublist, ofd)

    assert(sublist)

if __name__ == '__main__':
    test_gen_bids_sublist("test/rs_bucket_list.txt", "test/rs_subject_list.yml")

