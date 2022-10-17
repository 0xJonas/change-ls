from gen.generator import Generator
import gen.schema.types as t
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

        with open("lspscript/protocol/enumerations.py", "w", encoding="utf-8") as file:
            file.write(generator.generate_enumerations_py())
        with open("lspscript/protocol/structures.py", "w", encoding="utf-8") as file:
            file.write(generator.generate_structures_py())
