from .generator import Generator
import schema.types as t
import json


if __name__ == "__main__":
    with open("res/metaModel.json", encoding="utf-8") as file:
        raw = json.load(file)
        meta_model = t.MetaModel.from_json(raw)
        print(len(meta_model.structures))
        print(len(meta_model.notifications))
        print(len(meta_model.requests))
        print(len(meta_model.type_aliases))
        print(len(meta_model.enumerations))

        generator = Generator(meta_model)
        # print(generator.generate_structure_literal_definition(meta_model.structures[266].properties[0].type.content))
        generator.generate_anonymus_structure_definitions()
