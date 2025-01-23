Role Name
=========

curator-es-cleanup


Cleanup old logs from Elasticsearch cluster


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

- hosts: localhost
  roles:
    - role: curator-es-cleanup
      curator_es_cleanup_host_endpoint: 'demo.us-east-1.es.amazonaws.com'
      curator_es_cleanup_no_of_days: 15

License
-------

BSD

Author Information
------------------
Ranjith Gowder
