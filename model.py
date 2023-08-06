import json
import random
import requests

from label_studio_ml.utils import get_env, DATA_UNDEFINED_NAME
from label_studio_ml.model import LabelStudioMLBase


LABEL_STUDIO_HOST = get_env('LABEL_STUDIO_HOST', 'http://localhost:8080')
API_KEY = get_env('API_KEY')

print('=> LABEL STUDIO HOSTNAME = ', LABEL_STUDIO_HOST)
if not API_KEY:
    print('=> WARNING! API_KEY is not set')


class MyModel(LabelStudioMLBase):
    """This simple Label Studio ML backend demonstrates training & inference steps with a simple scenario:
    on training: it gets the latest created annotation and stores it as "prediction model" artifact
    on inference: it returns the latest annotation as a pre-annotation for every incoming task

    When connected to Label Studio, this is a simple repeater model that repeats your last action on a new task
    """
    def __init__(self, *args, **kwargs):
        # don't forget to initialize base class...
        super(MyModel, self).__init__(*args, **kwargs)
        print(f'Initialized model with project_id={self.project_id}')
        if self.get('parsed_label_config'):
            assert len(self.parsed_label_config) == 1
            self.from_name, self.info = list(self.parsed_label_config.items())[0]

            assert len(self.info['to_name']) == 1
            assert len(self.info['inputs']) == 1
            assert self.info['inputs'][0]['type'] == 'Image'

            self.to_name = self.info['to_name'][0]
            self.value = self.info['inputs'][0]['value']
            print(f'Initialized model with from_name={self.from_name}, to_name={self.to_name}, value={self.value}')

    def predict(self, tasks, context, **kwargs):
        """ Write your inference logic here
            :param tasks: [Label Studio tasks in JSON format](https://labelstud.io/guide/task_format.html)
            :param context: [Label Studio context in JSON format](https://labelstud.io/guide/ml.html#Passing-data-to-ML-backend)
            :return predictions: [Predictions array in JSON format](https://labelstud.io/guide/export.html#Raw-JSON-format-of-completed-tasks)
        """
        print(f'''\
        Run prediction on {tasks}
        Received context: {context}
        Project ID: {self.project_id}
        Label config: {self.label_config}
        Parsed JSON Label config: {self.parsed_label_config}''')

        if self.get('train_output'):
            train_output = self.get('train_output')
            prediction_result_example = json.loads(train_output)['prediction_example']
            prediction = prediction_result_example[-1]
            output_prediction = [{
                'result': prediction,
                'score': random.uniform(0, 1)
            }] * len(tasks)
            return output_prediction
        else:
            output_prediction = []
        print(f'Return output prediction: {json.dumps(output_prediction, indent=2)}')
        return output_prediction

    def _get_annotated_dataset(self, project_id):
        """Just for demo purposes: retrieve annotated data from Label Studio API"""
        download_url = f'{LABEL_STUDIO_HOST.rstrip("/")}/api/projects/{project_id}/export'
        response = requests.get(download_url, headers={'Authorization': f'Token {API_KEY}'})
        if response.status_code != 200:
            raise Exception(f"Can't load task data using {download_url}, "
                            f"response status_code = {response.status_code}")
        return json.loads(response.content)

    def fit(self, event, data,  **kwargs):
        print("FIT")
        """
        This method is called each time an annotation is created or updated
        You can run your logic here to update the model and persist it to the cache
        It is not recommended to perform long-running operations here, as it will block the main thread
        Instead, consider running a separate process or a thread (like RQ worker) to perform the training
        :param event: event type can be ('ANNOTATION_CREATED', 'ANNOTATION_UPDATED')
        :param data: the payload received from the event (check [Webhook event reference](https://labelstud.io/guide/webhook_reference.html))
        """
        tasks = self._get_annotated_dataset(self.project_id)
        input_images = []
        annotations =[]
        for task in tasks:
            if not task.get('annotations'):
                continue
        
            annotation = task['annotations'][0]
            if annotation.get('skipped') or annotation.get('was_cancelled'):
                continue
            # caminho da imagem
            input_image = task['data'].get(self.value) or task['data'].get(DATA_UNDEFINED_NAME)
            input_images.append(input_image)
            
            # obtendo a anotação
            annotations.append(annotation['result'])
            
        train_output = {
            'prediction_example': annotations,
            'also you can put': 'any artefact here'
        }

        self.set('train_output', json.dumps(train_output))
