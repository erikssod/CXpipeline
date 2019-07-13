#!/usr/bin/env python3.6

import yaml, logbook, sys, code

# Set up logging
logbook.StreamHandler(sys.stdout).push_application()
logger = logbook.Logger(__name__)
logbook.set_datetime_format('local')

print('Yes, we can use the print function')
logger.info('But logging is better in every way')

# Open config file
with open('../conf.yaml','r') as f:
    cfg = yaml.load(f)

# List some bits of the config fie
logger.info(cfg['data'])
logger.info(cfg['data']['example_data'])

# Define what file to read in
infile = cfg['data']['example_data']

# Read in file
with open(infile,'r') as f:
    data = f.read()

# Check what type of data it is
logger.info(f'Data is {type(data)}')

# Show a few lines of the data
logger.info(data[2:62])

# Remind ourselves what we are looking for
search_terms = cfg['lookfor']
logger.info(f'We are going to count occurances of {search_terms}')

# Loop over search terms and report findings
for index,content in enumerate(search_terms):
    logger.debug(f'Loop counter: {index}')
    logger.info(f'Looking for {content}')
    c = data.count(content)
    logger.info(f'Found {c} occurances of {content}')

logger.info('That\'s it for now. Next we\'ll look at some other ways to search for patterns using e.g. https://pypi.org/project/parse/')

# Debugging stuff.
#code.interact(local=locals())
