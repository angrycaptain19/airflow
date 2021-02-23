## CI pipeline

CI pipeline is created by enabling `.Values.git.dags`. It creates `initcontainer` for the clone and sync. It syncs the repository every 60 seconds by running `git pull origin master`


## Furter extensions

- Enable Prometheus metrics
- Configure email notification in order to alert in case of any failure
- Secure airflow web ui by creating ssl cert
- Enable LDAP authentication
- Make use of KubernetesPodOperator. Create an image with all functions and run them in a container.
- Extend the ETL pipeline


## Additional information

In `customer_number.csv` there were some events in `storenr` column with value `805`. This could be intentional.

- If we want to keep these rows, the foreign key constrain has to be removed.
- Other option could be to remove those rows and we can make use of FK constains (just as I manually did) 
- Or extend the ETL pipeline with cleanup/transform task: `initialLoadStores >> cleanEvents >> initialLoadEvents`

### Disable DAGS are paused at creation flag

By default, DAGS are paused at creation `dags_are_paused_at_creation=True` in `airflow.cfg`. In order to override it add `extraEnvVars` to `web` component in `values.yml`
`
  extraEnvVars:
    - name: AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION
      value: "false"
`

### Securely store database secrets

Database secrets are stored in k8s secret  `database-secrets.yml` and added in `values.yml`. In that way, pods will have the database secrets as environment variables. In `dags/dag.py` the database secrets can be accessed through `os.environ`.

`
  ## Secret with extra environment variables
  ##
  extraEnvVarsSecret: database-secrets
`

### Access data in container

In order to access data, add and extra volume mount. In that way, data will be available inside the container at the specified `mountPath`

`
  extraVolumeMounts:
    - name: git-cloned-dag-files-airflow
      mountPath: /opt/bitnami/airflow/dags/git-airflow/data
`
