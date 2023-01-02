from indi_aws import fetch_creds
import os

if __name__ == "__main__":
    s3_bucket = "fcp-indi"
    s3_creds = "/Users/cameron.craddock/AWS/ccraddock-fcp-indi-keys2.csv"
    s3_prefix = "data/Projects/ADHD200/RawDataBIDS"
    s3_sitedirs = ["Brown","KKI","NeuroIMAGE","NYU","OHSU","Peking_1","Peking_2","Peking_3","Pittsburgh","WashU"]
    out_prefix = "data/ADHD200/RawDataBIDS"
    max_subjs = 4

    if s3_creds:
        if not os.path.isfile(s3_creds):
            raise IOError("Could not filed aws_input_creds (%s)" % (s3_creds))

    from indi_aws import fetch_creds
    bucket = fetch_creds.return_bucket(s3_creds,s3_bucket)

    for site in s3_sitedirs:
        subjects=[]

        prefix=os.path.join(s3_prefix,site)
        print "gathering files from S3 bucket (%s) for %s" % (bucket, prefix)

        for s3_obj in bucket.objects.filter(Prefix=prefix):
            if 'T1w' in str(s3_obj.key) or 'bold' in str(s3_obj.key):
                fname = os.path.basename(str(s3_obj.key))
                if "sub-" not in fname:
                    if not os.path.exists(os.path.dirname(s3_obj.key).replace(s3_prefix,out_prefix)):
                        print "making the directory"
                        os.makedirs(os.path.dirname(s3_obj.key).replace(s3_prefix,out_prefix))
                    print "downloading %s to %s"%(str(s3_obj.key),str(s3_obj.key).replace(s3_prefix,out_prefix))
                    bucket.download_file(s3_obj.key,str(s3_obj.key).replace(s3_prefix,out_prefix))
                else:
                    pvals=os.path.dirname(str(s3_obj.key)).split('/')
                    subid=[s for s in pvals if 'sub-' in s]
                    if len(subid) > 1:
                        print("Why did it return so many (%d) subjects? (%s)"%(len(subid), str(subid)))
                    if len(subjects) < max_subjs:
                        subjects.append(subid)
                    if subid in subjects:
                        if not os.path.exists(os.path.dirname(s3_obj.key).replace(s3_prefix, out_prefix)):
                            print "making the directory"
                            os.makedirs(os.path.dirname(s3_obj.key).replace(s3_prefix, out_prefix))
                        print "downloading %s to %s" % (str(s3_obj.key), str(s3_obj.key).replace(s3_prefix, out_prefix))
                        bucket.download_file(s3_obj.key, str(s3_obj.key).replace(s3_prefix, out_prefix))
                        #s3_obj.key.get_contents_to_filename(str(s3_obj.key).replace(s3_prefix, out_prefix))
