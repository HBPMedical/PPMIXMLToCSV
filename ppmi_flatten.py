import glob 
import xmltodict
from collections import OrderedDict
import json
import re

def getField(subject, path):
    value = subject
    for p in path:
        try:
            value = value[p]
            if value == None:
                return None
        except KeyError:
            return None
    return value

def flatten(subject):
    output = OrderedDict()
    # field names and  corresponding path for the flatten
    fields = OrderedDict()
    fields['projectIdentifier']=['projectIdentifier']
    fields['projectDescription']=['projectDescription']
    fields['siteKey']=['siteKey']
    fields['subjectIdentifier']=['subject', 'subjectIdentifier']
    fields['researchGroup']=['subject', 'researchGroup']
    fields['subjectSex']=['subject', 'subjectSex']
    fields['visitIdentifier']=['subject', 'visit', 'visitIdentifier']
    fields['assessmentName']=['subject', 'visit', 'assessment', '@name']
    fields['assessmentComponentName']=['subject', 'visit', 'assessment', 'component', '@name']
    fields['assessmentScoreAtribute']=['subject', 'visit', 'assessment', 'component', 'assessmentScore', '@attribute']
    fields['assessmentScoreValue']=['subject', 'visit', 'assessment', 'component', 'assessmentScore', '#text']
    fields['studyIdentifier']=['subject', 'study', 'studyIdentifier']
    fields['subjectAge']=['subject', 'study', 'subjectAge']
    fields['ageQualifier']=['subject', 'study', 'ageQualifier']
    fields['weightKg']=['subject', 'study', 'weightKg']
    fields['postMortem']=['subject', 'study', 'postMortem']
    fields['seriesIdentifier']=['subject', 'study', 'series', 'seriesIdentifier']
    fields['modality']=['subject', 'study', 'series', 'modality']
    fields['dateAcquired']=['subject', 'study', 'series', 'dateAcquired']
    fields['imageUID']=['subject', 'study', 'series', 'imagingProtocol', 'imageUID']
    fields['seriesDescription']=['subject', 'study', 'series', 'imagingProtocol', 'description']
    fields['protocolTerms']=['subject', 'study', 'series', 'imagingProtocol', 'protocolTerm','protocol']
        
    for key, path in fields.iteritems():        
        output[key]=getField(subject, path)        
    return output

print 'opening and flatening xml files'
files = glob.glob('./PPMI-xml/*.xml')
data = []
for f in files:
    with open(f) as f:
        visit = xmltodict.parse(f.read())
        subject = visit['idaxs']['project']
        data.append(flatten(subject))

print 'flatening protocol terms'
for line in data:
    pt = line['protocolTerms']
    if pt:
        for term in pt:
            value = None
            if '#text' in term:
                value = term['#text']
            line[term['@term'].replace(' ', '_').lower()] = value
    else:
        line['acquisition_type'] = None
        line['weighting'] = None
        line['pulse_sequence'] = None
        line['slice_thickness'] = None
        line['te'] = None
        line['tr'] = None
        line['ti'] = None
        line['coil'] = None
        line['flip_angle'] = None
        line['acquisition_plane'] = None
        line['matrix_x'] = None
        line['matrix_y'] = None
        line['matrix_z'] = None
        line['pixel_spacing_x'] = None
        line['pixel_spacing_y'] = None
        line['manufacturer'] = None
        line['mfg_model'] = None
        line['field_strength'] = None
    del line['protocolTerms']

#converts the name to a more sql like (CamelCase -> camel_case)
def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

header = data[0].keys()
new_header = [ '"%s"' % convert(h) for h in header]
print 'generating final csv file'
with open("ppmi_out2.csv", "w") as f:
    f.write(",".join(new_header) + "\n")
    for line in data:
        values = [json.dumps(line[h]) for h in header]
        f.write(",".join(values) + "\n")
