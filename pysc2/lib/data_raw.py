from s2clientprotocol import sc2api_pb2 as sc_pb
import distutils.version
import pkgutil


def get_data_raw(version):
    data_raw = sc_pb.ResponseData()
    if distutils.version.LooseVersion(version) >= distutils.version.LooseVersion('4.7.1'):
        data = pkgutil.get_data('pysc2', f'lib/data/data_raw_{version}.serialized')
        data_raw.ParseFromString(data)
    elif distutils.version.LooseVersion(version) >= distutils.version.LooseVersion('4.0'):
        data_4_0 = pkgutil.get_data('pysc2', 'lib/data/data_raw_4_0.serialized')
        data_raw.ParseFromString(data_4_0)
    else:
        data_3_16 = pkgutil.get_data('pysc2', 'lib/data/data_raw_3_16.serialized')
        data_raw.ParseFromString(data_3_16)
    return data_raw
