""" Variable for the application"""
regex_date = r"(^\d{4}$)|" \
             r"(^\d{4}-(0[1-9]|1[0-2])$)|" \
             r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)|" \
             r"(^$)|" \
             r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])\/\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)"
params_search_taxon = ['q', 'nc__status__exact', 'rang__rang__exact', 'valide']
params_search_sample = ['q', 'toponyme']
#  TO update when a new rank is inserted in the database
param_hierarchy = [
    [1, 'Dumm'], [2, 'SPRG'], [3, 'KD'], [4, 'SSRG'], [5, 'IFRG'], [6, 'PH'], [7, 'SBPH'], [8, 'IFPH'], [9, 'SPCL'],
    [10, 'CL'], [11, 'SBCL'], [12, 'IFCL'], [13, 'SPOR'], [14, 'OR'], [15, 'SBOR'], [16, 'IFOR'], [23, 'SC'],
    [23, 'SCO'], [24, 'SSCO'], [17, 'SPFM'], [18, 'FM'], [19, 'SBFM'], [20, 'TR'], [21, 'SBTR'], [22, 'GN'],
    [22, 'SSGN'], [25, 'ES'], [26, 'SSES'], [27, 'VAR'], [28, 'SVAR']
]