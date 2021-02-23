# Infrastructure Engineer Case Study

## Provision Kubernetes cluster

`kind create cluster --config kind-config.yml`

## Deploy Airflow on the cluster along with database

`kubectl apply -f database-secrets.yml`
`helm install airflow bitnami/airflow --values values.yaml`

`kubectl get nodes --namespace default -o jsonpath="{.items[0].status.addresses[0].address}"`

`kubectl get --namespace default -o jsonpath="{.spec.ports[0].nodePort}" services airflow`

Wait till apps are ready

`kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=airflow --timeout=3600s`

Once all pods are up and running, open `http://172.18.0.3:31759/` in a browser

Login with `user` username and for retrieving the password execute the following command:

`kubectl get secret --namespace "default" airflow -o jsonpath="{.data.airflow-password}" | base64 --decode`


## Use Airflow to load data from the `data/` directory to the database

Trigger `initial_load_dag` DAG.


Get the database password by running:

`
kubectl get secret --namespace "default" database-secrets -o jsonpath="{.data.POSTGRESQLPASSWORD}" | base64 --decode`
`

When pipline is completed check the table content in PostgreSQL:

`
kubectl exec -it airflow-postgresql-0 bash
I have no name!@airflow-postgresql-0:/$ psql -U bn_airflow -d bitnami_airflow -c 'select * from stores'
I have no name!@airflow-postgresql-0:/$ psql -U bn_airflow -d bitnami_airflow -c 'select * from events'
`

