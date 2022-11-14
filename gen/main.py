from gen.generator import Generator
import gen.schema.types as t
import json
from pathlib import Path


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

        static_dir = Path("./gen/static/")
        assert static_dir.is_dir()
        for d in static_dir.iterdir():
            if not d.suffix == "py":
                continue
            with open(d) as input, open(f"lspscript/generated/{d.name}", "w") as output:
                output.write(input.read())

        with open("lspscript/generated/enumerations.py", "w", encoding="utf-8") as file:
            file.write(generator.generate_enumerations_py())
        with open("lspscript/generated/structures.py", "w", encoding="utf-8") as file:
            file.write(generator.generate_structures_py())
        with open("lspscript/generated/client_requests.py", "w", encoding="utf-8") as file:
            file.write(generator.generate_client_requests_py())
