import os
import kopf
import kubernetes
import yaml

def create_mysql_deployment(namespace, name, image, password, database):

  deployment_template_path = os.path.join(os.path.dirname(__file__), 'deployment_template.yaml')
  deployment_template = open(deployment_template_path, 'rt').read()
  processed_deployment_template = deployment_template.format(
    name=name,
    image=image,
    password=password,
    database=database
  )
  deployment_yaml = yaml.safe_load(processed_deployment_template)
  kopf.adopt(deployment_yaml)

  api = kubernetes.client.AppsV1Api()
  obj = api.create_namespaced_deployment(
      namespace=namespace,
      body=deployment_yaml
  )

  return

def patch_mysql_deployment(namespace, deployment_name, image):

  deployment_patch = {'spec': {'template': {'spec': {'containers': [{'name': 'mysql', 'image': image}]}}}}

  api = kubernetes.client.AppsV1Api()
  obj = api.patch_namespaced_deployment(
    name=deployment_name,
    namespace=namespace,
    body=deployment_patch
  )

  return

def create_mysql_service(namespace, name):

  service_template_path = os.path.join(os.path.dirname(__file__), 'service_template.yaml')
  service_template = open(service_template_path, 'rt').read()
  processed_service_template = service_template.format(
    name=name
  )
  serviсe_yaml = yaml.safe_load(processed_service_template)
  kopf.adopt(serviсe_yaml)

  api = kubernetes.client.CoreV1Api()
  obj = api.create_namespaced_service(
     namespace=namespace,
     body=serviсe_yaml
  )

  return

def create_mysql_pvc(namespace, name, storage_size):
   
  pvc_template_path = os.path.join(os.path.dirname(__file__), 'pvc_template.yaml')
  pvc_template = open(pvc_template_path, 'rt').read()
  processed_pvc_template = pvc_template.format(
    name=name,
    storage_size=storage_size
  )
  pvc_yaml = yaml.safe_load(processed_pvc_template)
  kopf.adopt(pvc_yaml)

  api = kubernetes.client.CoreV1Api()
  obj = api.create_namespaced_persistent_volume_claim(
     namespace=namespace,
     body=pvc_yaml
  )

  return

@kopf.on.create('mysql')
def create_custom_resource(spec, name, namespace, logger, **kwargs):
  image = spec.get('image')
  database = spec.get('database')
  password = spec.get('password')
  storage_size =  spec.get('storage_size')

  create_mysql_pvc(namespace, name, storage_size)
  logger.info(f"PersistentVolumeClaim {name} was successfully created")

  create_mysql_deployment(namespace, name, image, password, database)
  logger.info(f"Deployment {name} was successfully created")

  create_mysql_service(namespace, name)
  logger.info(f"Service {name} was successfully created")

  return {'deployment-name': name}

@kopf.on.update('mysql')
def update_custom_resource(spec, status, namespace, logger, **kwargs):
  image = spec.get('image')
  deployment_name = status['create_custom_resource']['deployment-name']
  patch_mysql_deployment(namespace, deployment_name, image)
  logger.info(f"Deployment {deployment_name} was successfully updated")
