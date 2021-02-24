#
# Copyright (c) 2021 Czech Technical University in Prague.
#
# This file is part of Roadmaptools 
# (see https://github.com/aicenter/roadmap-processing).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from shapely.geometry import LineString, Point

line = LineString([(0,0),(0,3),(2,3),(2,0)])

pointa = Point(0,3)
pointb = Point(2,1)


print("Point A distance along linestring: {}".format(line.project(pointa)))
print("Point B distance along linestring: {}".format(line.project(pointb)))


line = LineString([(0,0),(0,3),(0,0),(4,0)])

pointa = Point(1,0)
pointb = Point(0,2)


print("Point A distance along linestring: {}".format(line.project(pointa)))
print("Point B distance along linestring: {}".format(line.project(pointb)))

line = LineString([(459401.4808268753, 5548751.413400644), (459416.9239635981, 5548756.833431144), (459452.9326752117, 5548768.679952354), (459471.5841274337, 5548771.740767008), (459486.558864173, 5548769.180983176), (459513.0016597167, 5548773.317026346), (459574.6251330864, 5548782.979997741), (459591.624302734, 5548787.032218366), (459598.1756266461, 5548794.41028268), (459609.8542174158, 5548792.075914356), (459675.927428248, 5548825.512556223), (459688.8854083499, 5548840.103200087), (459708.2701523154, 5548848.440909361), (459724.7171202758, 5548855.19967219), (459729.901486638, 5548857.784718673), (459744.6238166057, 5548864.46758783), (459764.0928814765, 5548872.626955694), (459790.2458894122, 5548883.982884461), (459792.5860938389, 5548885.066070594), (459800.8128602093, 5548888.895875888), (459808.1502022735, 5548892.409928492), (459809.9814406136, 5548893.352401712), (459820.8413175698, 5548898.218752398), (459818.6454109197, 5548904.906766911), (459813.970836277, 5548918.729692562), (459813.138770355, 5548921.282240469), (459809.3071075905, 5548938.745918109), (459807.8724938399, 5548954.390261103), (459808.7382261936, 5548973.430884821), (459811.9416467017, 5548990.374639822), (459817.0341712576, 5549011.2070169), (459823.7416443196, 5549038.476372919), (459826.8347908729, 5549049.327661606), (459830.7286573184, 5549062.97496253), (459832.8479212601, 5549069.886271794), (459819.8982116348, 5549076.243740443), (459798.0287004329, 5549083.591244955), (459792.8225462207, 5549084.731221056), (459782.6278883351, 5549088.366089093), (459776.1627358288, 5549094.252326386), (459770.0328825607, 5549103.81649292), (459401.4808268753, 5548751.413400644), (459330.3869575746, 5548725.079012355), (459401.4808268753, 5548751.413400644)])

pointa = Point(459428.2239730014, 5548760.551026001)
pointb = Point(459361.8893196194, 5548736.74802745)

print("Point A distance along linestring: {}".format(line.project(pointa)))
print("Point B distance along linestring: {}".format(line.project(pointb)))

a = 1