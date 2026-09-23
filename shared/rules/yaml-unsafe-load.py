import yaml

document = "!!python/object/apply:os.system ['id']"

# ruleid: bugledger-yaml-unsafe-load
yaml.load(document)

# ruleid: bugledger-yaml-unsafe-load
yaml.load(document, Loader=yaml.Loader)

# ruleid: bugledger-yaml-unsafe-load
yaml.load_all(document, Loader=yaml.UnsafeLoader)

# ruleid: bugledger-yaml-unsafe-load
yaml.unsafe_load(document)

# ok: bugledger-yaml-unsafe-load
yaml.safe_load(document)

# ok: bugledger-yaml-unsafe-load
yaml.load(document, Loader=yaml.SafeLoader)

# ok: bugledger-yaml-unsafe-load
yaml.load(document, Loader=yaml.CSafeLoader)

# ok: bugledger-yaml-unsafe-load
yaml.load(document, Loader=yaml.FullLoader)
