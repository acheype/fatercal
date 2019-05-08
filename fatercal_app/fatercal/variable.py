""" Variable for the application"""
regex_date = r"(^\d{4}$)|" \
             r"(^\d{4}-(0[1-9]|1[0-2])$)|" \
             r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)|" \
             r"(^$)|" \
             r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])\/\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)"
#  TO update when a new rank is inserted in the database
param_hierarchy = [
    [1, 'Dumm'], [2, 'SPRG'], [3, 'KD'], [4, 'SSRG'], [5, 'IFRG'], [6, 'PH'], [7, 'SBPH'], [8, 'IFPH'], [9, 'SPCL'],
    [10, 'CL'], [11, 'SBCL'], [12, 'IFCL'], [13, 'SPOR'], [14, 'OR'], [15, 'SBOR'], [16, 'IFOR'], [17, 'SC'],
    [18, 'SCO'], [19, 'SSCO'], [20, 'SPFM'], [21, 'FM'], [22, 'SBFM'], [23, 'TR'], [24, 'SBTR'], [25, 'GN'],
    [26, 'SSGN'], [27, 'ES'], [28, 'SSES'], [29, 'VAR'], [30, 'SVAR']
]