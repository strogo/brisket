from django.utils.functional import curry
import base64, urllib


def get_crp_url(type, standardized_name, ids, cycle=None):
    if (type == 'politician' and 'urn:crp:recipient' in ids) or type != 'politician':
        return "http://www.opensecrets.org/usearch/index.php?q=%s" % standardized_name
    return None

def get_nimsp_url(type, standardized_name, ids, cycle):
    if type == 'organization' and 'urn:nimsp:organization' in ids:
        if cycle:
            return "http://www.followthemoney.org/database/topcontributor.phtml?u=%(id)s&y=%(cycle)s" % dict(id=ids['urn:nimsp:organization'], cycle=cycle)
        else:
            return "http://www.followthemoney.org/database/topcontributor.phtml?u=%(id)s" % dict(id=ids['urn:nimsp:organization'])
    elif type == 'politician' and 'urn:nimsp:recipient' in ids:
        return "http://www.followthemoney.org/database/uniquecandidate.phtml?uc=%(id)s" % dict(id=ids['urn:nimsp:recipient'])
    return None

def get_td_url(type, standardized_name, ids, cycle):
    keywords = {'individual': 'contributor_ft', 'organization': 'organization_ft', 'politician': 'recipient_ft'}
    query_string = "%s=%s" % (keywords[type], standardized_name)
    if cycle:
        query_string += "&cycle=%s" % cycle
    return "http://transparencydata.com/contributions/#%s" % base64.b64encode(query_string)

def get_links(type, standardized_name, namespaces_and_ids, cycle):
    """ Return a list of (label, url) pairs for an organization. """
    
    ids = dict([(item['namespace'], item['id']) for item in namespaces_and_ids])
    if cycle == '-1':
        cycle = None

    links = [
        dict(text='OpenSecrets.org', url=get_crp_url(type, standardized_name, ids, cycle)),
        dict(text='FollowTheMoney.org', url=get_nimsp_url(type, standardized_name, ids, cycle)),
        dict(text='TransparencyData.com', url=get_td_url(type, standardized_name, ids, cycle)),
    ]
    
    links = filter(lambda link: link['url'] is not None, links)

    return links


get_organization_links = curry(get_links, 'organization')
get_individual_links = curry(get_links, 'individual')
get_politician_links = curry(get_links, 'politician')

def get_lobbying_links(type, standardized_name, ids, cycle):
    # TD
    td_types = {'firm': 'registrant_ft', 'lobbyist': 'lobbyist_ft', 'client': 'client_ft'}
    td_params = {}
    if cycle != '-1':
        td_params['year'] = "%s|%s" % (int(cycle) - 1, cycle)
    
    td_params[td_types[type]] = standardized_name
    
    links = [
        dict(text='TransparencyData.com', url="http://transparencydata.com/lobbying/#%s" % base64.b64encode(urllib.urlencode(td_params)))
    ]
    
    # OpenSecrets
    os_types = {'firm': 'f', 'lobbyist': 'l', 'client': 'c'}
    if type == 'lobbyist':
        indiv_ids = filter(lambda s: s['namespace'] == 'urn:crp:individual', ids)
        if indiv_ids:
            os_params = {'lname': standardized_name, 'id': indiv_ids[0]['id']}
            if cycle != '-1':
                os_params['year'] = cycle
            links.append(
                dict(text='OpenSecrets.orgs', url="http://www.opensecrets.org/lobby/lobbyist.php?%s" % urllib.urlencode(os_params))
            )
    
    else:
        links.append(
            dict(text='OpenSecrets.org', url="http://www.opensecrets.org/lobby/lookup.php?%s" % urllib.urlencode({'type': os_types[type], 'lname': standardized_name}))
        )
    
    return links