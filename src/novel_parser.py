from yaml import safe_load
from jsonschema import validate, ValidationError
from pathlib import Path


class NovelParser:
    schema = {
        "type": "object",
        "properties": {
            "fork": {
                "type": "object",
                "properties": {
                    "incoming": {"type": "string"},
                    "img": {"type": "string"},
                    "text": {"type": "string"},
                    "next": {
                        "type": "array",
                        "items": {"$ref": "#/properties/fork"}
                    }
                },
                "required": ["incoming", "img"],
                "additionalProperties": False
            }
        },
        "required": ["fork"],
        "additionalProperties": False
    }


    def __init__(self, config_path, images_path):
        self.config = self.parse_novel(config_path, images_path)
    
    def __iter__(self):
        self._generator = self._get_next(self.config['fork'], '0')
        return self
    
    def __next__(self):
        return next(self._generator)
    
    
    @classmethod
    def parse_novel(cls, config_path, images_path):
        images_path = Path(images_path)

        # assert text config
        with open(config_path) as f:
            yaml_conf = safe_load(f)
        try: 
            validate(yaml_conf, cls.schema)
        except ValidationError as e:
            raise Exception("Invalid novel configuration:", e.message)

        # assert given images are present
        def _resolve_image(conf):
            if (img := conf.get('img')) is not None:
                if not (images_path / img).exists():
                    raise Exception(f"Image {str(images_path / img)} not found")
            if (next := conf.get('next')) is not None:
                for n in next:
                    _resolve_image(n)

        _resolve_image(yaml_conf['fork'])

        return yaml_conf


    def _get_next(self, conf, cur_idx, prev_idx=None):
        res = {}

        # add display data
        for field in ('incoming', 'text', 'img'):
            res[field] = conf.get(field)

        res['cur'] = cur_idx
        res['prev'] = prev_idx

        # add data about next replicas
        next_confs = conf.get('next')
        if next_confs is not None:
            next_res = []
            for n_idx, n in enumerate(next_confs):
                next_idx = cur_idx + '.' + str(n_idx)
                yield from self._get_next(n, next_idx, cur_idx)
                next_res.append((n['incoming'], next_idx))
            res['next'] = tuple(next_res)

        yield res