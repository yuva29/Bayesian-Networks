# -*- coding: cp1252 -*-
import sys
import json

EXPECTED_ARGS_LEN = 3
diseases = []
disease_finding_count = {}
disease_prob = {}
disease_findings = {}
findings_given_disease = {}
findings_given_not_disease = {}
original_disease_findings = {}
output_file = ''

""" Results """
q1 = {}
q2 = {}
q3 = {}

def calc_prob(disease_id, test_results, patient_id):
    dname = diseases[disease_id]
    """print "Calculating prob. of disease ", dname , " for patient ", patient_id"""
    finding_prob_given_disease = findings_given_disease[dname]
    finding_prob_given_not_disease = findings_given_not_disease[dname]
    finding_count = disease_finding_count[dname]

    """ Probability of patient not having the disease and Probility of patient having the disease """
    prob_pat_not_having_disease = 1-float(disease_prob[dname])
    prob_pat_having_disease = float(disease_prob[dname])
    for i in range(0, int(finding_count)):
        temp_not_prob = float(finding_prob_given_not_disease[i])
        temp_prob = float(finding_prob_given_disease[i])
        if test_results[i] == "T":
            prob_pat_not_having_disease*=temp_not_prob
            prob_pat_having_disease*=temp_prob
        elif test_results[i] == "F":
            prob_pat_not_having_disease*=(1-temp_not_prob)
            prob_pat_having_disease*=(1-temp_prob)

    """ Set up variables to calculate min and max possible probabilities """
    min_prob_pat_having_disease = prob_pat_having_disease
    min_prob_pat_not_having_disease = prob_pat_not_having_disease
    max_prob_pat_having_disease = prob_pat_having_disease
    max_prob_pat_not_having_disease = prob_pat_not_having_disease

    """ To calculate the tests required to carry out for a patient """
    min_index = -1
    max_index = -1
    max_value = 'N'
    min_value = 'N'
    
    # Original probability of the disease 
    org_alpha = 1/(prob_pat_having_disease+prob_pat_not_having_disease)
    org_prob = prob_pat_having_disease*org_alpha
    max_prob_val = org_prob
    min_prob_val = org_prob    

    df = disease_findings[dname]
    for i in range(0, int(finding_count)):
        temp_prob = float(finding_prob_given_disease[i])
        temp_not_prob = float(finding_prob_given_not_disease[i])
        if test_results[i] == "U":
            """ Calculate the prob. assuming that the unknown test is 'T' """
            temp_alpha1 = 1/((min_prob_pat_having_disease*temp_prob)+(min_prob_pat_not_having_disease*temp_not_prob))
            temp1 = (min_prob_pat_having_disease*temp_prob)*temp_alpha1
            """ Calculate the prob. assuming that the unknown test is 'F' """
            temp_alpha2 = 1/((min_prob_pat_having_disease*(1-temp_prob))+(min_prob_pat_not_having_disease*(1-temp_not_prob)))
            temp2 = (min_prob_pat_having_disease*(1-temp_prob))*temp_alpha2
            """ Compare both the probabilities and find the min and max """
            if temp1>temp2: #temp2 prob < temp1
                min_prob_pat_having_disease*=(1-temp_prob)
                min_prob_pat_not_having_disease*=(1-temp_not_prob)
                max_prob_pat_having_disease*= temp_prob
                max_prob_pat_not_having_disease*=temp_not_prob                    
            else: #temp2 is greater
                min_prob_pat_having_disease*= temp_prob
                min_prob_pat_not_having_disease*=temp_not_prob
                max_prob_pat_having_disease*=(1-temp_prob)
                max_prob_pat_not_having_disease*=(1-temp_not_prob)
           
            """ for Q3 """            
            """ Calculate the prob. assuming that the unknown test is 'T' """
            temp_alpha1 = 1/((prob_pat_having_disease*temp_prob)+(prob_pat_not_having_disease*temp_not_prob))
            temp1 = (prob_pat_having_disease*temp_prob)*temp_alpha1
            """ Calculate the prob. assuming that the unknown test is 'F' """
            temp_alpha2 = 1/((prob_pat_having_disease*(1-temp_prob))+(prob_pat_not_having_disease*(1-temp_not_prob)))
            temp2 = (prob_pat_having_disease*(1-temp_prob))*temp_alpha2
                       
            if temp1>max_prob_val: # finding is considered TRUE in temp1
                max_prob_val = temp1
                max_index = i
                max_value = 'T'
            if temp2>max_prob_val:
                max_prob_val = temp2
                max_index = i
                max_value = 'F'                
            if temp1<min_prob_val:
                min_prob_val = temp1
                min_index = i
                min_value = 'T'
            if temp2<min_prob_val: # finding is considered FALSE in temp2
                min_prob_val = temp2
                min_index = i
                min_value ='F'                               
                    
    """ Actual probabilty based on the test result """
    actual_alpha = 1/((prob_pat_having_disease)+prob_pat_not_having_disease)
    actual_result = round(prob_pat_having_disease*actual_alpha, 4)
    actual_result = "{:0.4f}".format(actual_result) # to align with 4 decimal places

    """ Mininum probabilty possible """    
    min_alpha = 1/((min_prob_pat_having_disease)+(min_prob_pat_not_having_disease))
    min_result = round((min_prob_pat_having_disease)*min_alpha, 4)
    min_result = "{:0.4f}".format(min_result) # to align with 4 decimal places

    """ Maximum probabilty possible """
    max_alpha = 1/((max_prob_pat_having_disease)+(max_prob_pat_not_having_disease))
    max_result = round((max_prob_pat_having_disease)*max_alpha, 4)
    max_result = "{:0.4f}".format(max_result) # to align with 4 decimal places
    
    """ Find the test that's required must and not """
    findings = disease_findings[dname]
    recommended_tests = []
    
    if max_index != -1:
        recommended_tests.append(findings[max_index])
    else: # incase if there are no "U" tests
        recommended_tests.append('none')
    recommended_tests.append(max_value)
    
    if min_index != -1:
        recommended_tests.append(findings[min_index])
    else: # incase if there are no "U" tests
        recommended_tests.append('none')
    recommended_tests.append(min_value)
    
    """print "Min Result:", min_result, max_result, dname, patient_id"""
    return (actual_result, [min_result, max_result], recommended_tests)

"""
To parse the input file
"""
def parse_file(input_file):
    base_data = (input_file.readline()).split()
    num_disease = int(base_data[0])
    num_patients = int(base_data[1])
    cur_patient = 1
    print "No.of Disease :", num_disease, " No.of Patients :", num_patients
    """Each disease has 4 lines of data """
    temp_num_disease = num_disease
    while temp_num_disease>0:
        """ Read the data about disease """
        disease_detail = input_file.readline().split()
        disease_finding = eval(input_file.readline())
        prob_findings_given_disease = eval(input_file.readline())
        prob_findings_given_not_disease = eval(input_file.readline())

        """ Sort the findings and their probabilites in alphabetical order """
        prob_findings_given_disease = [x for (y,x) in sorted(zip(disease_finding, prob_findings_given_disease))]
        prob_findings_given_not_disease = [x for (y,x) in sorted(zip(disease_finding, prob_findings_given_not_disease))]
        original_disease_finding = []
        # helps to sort the patients test results according to the finding order
        for f in disease_finding: 
            original_disease_finding.append(f)    
        disease_finding.sort()
        
        """ append the data to global lists """
        diseases.append(disease_detail[0])
        disease_finding_count[disease_detail[0]] = disease_detail[1]
        disease_prob[disease_detail[0]] = disease_detail[2]
        original_disease_findings[disease_detail[0]] = original_disease_finding
        disease_findings[disease_detail[0]] = disease_finding
        findings_given_disease[disease_detail[0]] = prob_findings_given_disease
        findings_given_not_disease[disease_detail[0]] = prob_findings_given_not_disease
        temp_num_disease-=1

    print "Diseases :", diseases
    for dname in diseases:
        print "\n"
        print "Disease Name :", dname
        print "Disease finding count :", disease_finding_count[dname]
        print "P(Disease) :", disease_prob[dname]
        print "Disease Findings :", disease_findings[dname]
        print "P(Findings|Disease) :", findings_given_disease[dname]
        print "P(Findings|~Disease) :", findings_given_not_disease[dname]

    """ Read data about patients test results """
    count = 0
    patient_id = 1
    while patient_id <= num_patients:
        temp_patient_actual_results = {}
        temp_patient_possible_results = {}
        temp_patient_recommended_tests = {}
        while count < num_disease:
            test_results = eval(input_file.readline())
            # sort the test results based on the finding
            org_disease_finding = original_disease_findings[diseases[count]]
            test_results = [x for (y,x) in sorted(zip(org_disease_finding, test_results))]
            actual_prob, min_max, recommended_tests = calc_prob(count, test_results, patient_id)
            temp_patient_actual_results[diseases[count]] = actual_prob
            temp_patient_possible_results[diseases[count]] = min_max
            temp_patient_recommended_tests[diseases[count]] = recommended_tests
            count+=1
        q1[patient_id] = temp_patient_actual_results
        q2[patient_id] = temp_patient_possible_results
        q3[patient_id] = temp_patient_recommended_tests
        count = 0
        patient_id+=1

    for i in range(1, num_patients+1):
        pat_id = 'Patient-'+str(i)+':'
        output_file.write(pat_id)
        output_file.write("\n")
        json.dump(q1[i], output_file)
        output_file.write("\n")
        json.dump(q2[i], output_file)
        output_file.write("\n")
        json.dump(q3[i], output_file)
        output_file.write("\n")
        
"""
Command line argument validation
"""
if EXPECTED_ARGS_LEN == len(sys.argv):
    if '-i' != sys.argv[1]:
        print "Malformed command. Usage : python bayes.py –i inputfilename"
    else:
        try:
            """ READ THE INPUT FILE """
            file_handler = open(sys.argv[2],'r')
            #temp = sys.argv[2].rsplit('/', 1)
            #temp = temp[1].split('.')
            temp = sys.argv[2].split('.')
            output_file = open(temp[0]+'_inference.'+temp[1], 'w+')            
            parse_file(file_handler)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
else:
    print "Malformed command. Usage : python bayes.py -i inputfilename"
    exit
