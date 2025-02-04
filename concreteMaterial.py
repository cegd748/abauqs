from abaqus import *
from abaqusConstants import *
from caeModules import *
from concrete import Concrete

DEFAULT_COMPRESSION = ((47.424, 0.0), (55.575, 0.000154333), (62.244, 0.000295092), (67.431, 0.00047248), (71.136, 0.0006865),
                       (73.359, 0.00093715), (74.1, 0.001224431), (74.03675771, 0.00153159), (73.56050407, 0.001848958),
                       (72.35346382, 0.002184388), (70.34486717, 0.00253963), (67.66992982, 0.002911343),
                       (64.56108708, 0.00329378), (61.25435421, 0.003681108), (57.93885076, 0.004068654),
                       (54.74333397, 0.004453233), (51.74309645, 0.004832986), (48.44873743, 0.005281128),
                       (44.94954407, 0.005807676), (41.3603193, 0.00642446), (37.80427793, 0.007146039),
                       (34.3937169, 0.007990758), (31.21471402, 0.008981838), (28.31982794, 0.010148397),
                       (25.72899911, 0.011526441), (23.43602621, 0.013159925), (21.4172131, 0.015101993),
                       (19.63956114, 0.017416535), (18.06716184, 0.020180125), (16.66548485, 0.023484439),
                       (15.40383126, 0.027439227), (14.25642116, 0.032175911), (13.20257295, 0.037851948),
                       (12.22633957, 0.044656064), (11.3158635, 0.052814552), (10.46262534, 0.062598822),
                       (9.660695932, 0.07433446), (8.906055634, 0.088412092), (8.196013129, 0.105300418),
                       (7.528734979, 0.125561842), (6.90288359, 0.149871228), (6.317353221, 0.179038401),
                       (5.7710895, 0.214035144), (5.262976476, 0.256027592), (4.791775637, 0.306415105),
                       (4.356102893, 0.366876914), (3.954431613, 0.43942809), (3.585112109, 0.526486716),
                       (3.246400196, 0.630954485), (2.936489425, 0.756313422), (2.653543286, 0.906741947),
                       (2.395724973, 1.087254158), (2.161223363, 1.30386696), (1.948274596, 1.56380063),
                       (1.755179127, 1.875719491), (1.580314508, 2.25002072))

DEFAULT_COMPRESSION_DAMAGE = ((0.0, 0.0), (0.051846379, 0.000154333), (0.083996578, 0.000295092), (0.117317016, 0.00047248),
                              (0.15194562, 0.0006865), (0.188049748, 0.00093715), (0.225835811, 0.001224431),
                              (0.262178464, 0.00153159), (0.295865377, 0.001848958), (0.329062661, 0.002184388),
                              (0.362505909, 0.00253963), (0.395945383, 0.002911343), (0.4287195, 0.00329378),
                              (0.460156351, 0.003681108), (0.489762164, 0.004068654), (0.517260545, 0.004453233),
                              (0.542558899, 0.004832986), (0.57007047, 0.005281128), (0.599273181, 0.005807676),
                              (0.629484848, 0.00642446), (0.65994389, 0.007146039), (0.689908463, 0.007990758),
                              (0.718745112, 0.008981838), (0.745984217, 0.010148397), (0.771334905, 0.011526441),
                              (0.7946668, 0.013159925), (0.815973292, 0.015101993), (0.835330443, 0.017416535),
                              (0.852860937, 0.020180125), (0.868707205, 0.023484439), (0.883013999, 0.027439227),
                              (0.895918761, 0.032175911), (0.907547443, 0.037851948), (0.918013705, 0.044656064),
                              (0.927419841, 0.052814552), (0.935858393, 0.062598822), (0.943413806, 0.07433446),
                              (0.950163828, 0.088412092), (0.956180571, 0.105300418), (0.961531223, 0.125561842),
                              (0.966278501, 0.149871228), (0.970480909, 0.179038401), (0.974192883, 0.214035144),
                              (0.977464883, 0.256027592), (0.980343462, 0.306415105), (0.982871357, 0.366876914),
                              (0.985087597, 0.43942809), (0.987027642, 0.526486716), (0.988723555, 0.630954485),
                              (0.990204192, 0.756313422), (0.991495411, 0.906741947), (0.992620297, 1.087254158),
                              (0.993599379, 1.30386696), (0.994450862, 1.56380063), (0.995190836, 1.875719491),
                              (0.995833489, 2.25002072))
DEFAULT_TENSION = ((4.514373525, 0.158449232), )
DEFAULT_TENSION_DAMAGE = 0
"""DEFAULT_TENSION = ((4.514373525, 0.0), (3.36017361, 9.29728e-05), (2.307271976, 0.000148335), (1.692310359, 0.000192873),
                   (1.080197131, 0.000266678), (0.62978239, 0.000395161), (0.399872433, 0.00057687),
                   (0.278661256, 0.000814568), (0.208131476, 0.001109688), (0.155409817, 0.001551057),
                   (0.113224711, 0.002285542), (0.084829424, 0.003313063), (0.065890533, 0.004633727),
                   (0.052854758, 0.006247623), (0.043539781, 0.008154803), (0.036650227, 0.010355301),
                   (0.031400764, 0.012849135), (0.02729872, 0.015636317))

DEFAULT_TENSION_DAMAGE = ((0.0, 0.0), (0.313105515, 9.29728e-05), (0.473030873, 0.000148335), (0.577837348, 0.000192873),
                          (0.698327094, 0.000266678), (0.805322377, 0.000395161), (0.870213198, 0.00057687),
                          (0.908431927, 0.000814568), (0.932069958, 0.001109688), (0.950296601, 0.001551057),
                          (0.965028996, 0.002285542), (0.974851109, 0.003313063), (0.981255763, 0.004633727),
                          (0.985541041, 0.006247623), (0.988513029, 0.008154803), (0.990647326, 0.010355301),
                          (0.992228267, 0.012849135), (0.993431105, 0.015636317))"""

DEFAULT_ELASTICITY = ((40458, 0.2), )
DEFAULT_PLASTICITY = ((38.0, 0.1, 1.16, 0.6667, 0.005), )
DEFAULT_DENSITY = ((2.5e-02,),)

class ConcreteMaterial:
    def __init__(self, concrete:Concrete, name='CDP',
                 elasticity=DEFAULT_ELASTICITY, plasticity=DEFAULT_PLASTICITY,
                 compression=DEFAULT_COMPRESSION, compressionDamage=DEFAULT_COMPRESSION_DAMAGE,
                 tension=DEFAULT_TENSION, tensionDamage=DEFAULT_TENSION_DAMAGE,
                 density= DEFAULT_DENSITY):
        self.name = name
        self.elasticity = elasticity
        self.plasticity = plasticity
        self.compression = compression
        self.compressionDamage = compressionDamage
        self.tension = tension
        self.tensionDamage = tensionDamage
        self.density = density
        self.__defineMaterial(concrete)
        self.__defineSection(concrete)
        self.__assignSection(concrete)

    def __defineMaterial(self, concrete:Concrete):
        mdb.models[concrete.model_name].Material(name=self.name)
        mdb.models[concrete.model_name].materials[self.name].Elastic(table=self.elasticity)
        mdb.models[concrete.model_name].materials[self.name].ConcreteDamagedPlasticity(table=self.plasticity)
        mdb.models[concrete.model_name].materials[self.name].concreteDamagedPlasticity.ConcreteCompressionHardening(table=self.compression)
        mdb.models[concrete.model_name].materials[self.name].concreteDamagedPlasticity.ConcreteCompressionDamage(table=self.compressionDamage)
        mdb.models[concrete.model_name].materials[self.name].concreteDamagedPlasticity.ConcreteTensionStiffening(table=self.tension, type=GFI)
        #mdb.models[concrete.model_name].materials[self.name].concreteDamagedPlasticity.ConcreteTensionStiffening(table=self.tension)
        #mdb.models[concrete.model_name].materials[self.name].concreteDamagedPlasticity.ConcreteTensionDamage(table=self.tensionDamage)
        mdb.models[concrete.model_name].materials[self.name].Density(table=self.density)

    def __defineSection(self, concrete:Concrete):
        mdb.models[concrete.model_name].HomogeneousSolidSection(name=self.name, material=self.name, thickness=None)

    def __assignSection(self, concrete:Concrete):
        p = mdb.models[concrete.model_name].parts[concrete.part_name]
        region = regionToolset.Region(cells=p.cells)
        p.SectionAssignment(region=region, sectionName=self.name, offset=0.0,
                            offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)