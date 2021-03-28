# the little less documented way of adding a custom node tree
#   and populate it with nodes of varying types of I/O
#   sockets that work together, discombobulated

# first we import the blender API
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
# from bpy_extras import view3d_utils
import math
import mathutils
from mathutils import Vector

v_ = '''
    in vec2 pos;
    out vec2 position;
    
    uniform mat4 ModelViewProjectionMatrix;
    
    void main()
    {
        position = pos;
        gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
    }
'''

f_ = '''
in vec2 position;
out vec4 fragColor;
uniform mat4 PersInv;
uniform mat4 ViewInv;
uniform vec3 CamLoc;
uniform vec3 LightLoc;
uniform vec2 Size;

#define PI 3.1415926535
#define EPSILON 0.001
#define UPPER 0.9999
#define MAX_MARCHING_STEPS 30
#define MIN_DIST 0.0
#define MAX_DIST 1000.0

float sphereSDF(vec3 samplePoint)
{
    return length(samplePoint) - 1.0;
}

float sceneSDF(vec3 samplePoint) 
{
    return sphereSDF(samplePoint);
}

vec3 calcNormal(vec3  p) { // for function f(p)
    const float h = 0.0001;// replace by an appropriate value
    const vec2 k = vec2(1, -1);
    return normalize(k.xyy*sceneSDF(p + k.xyy*h) +
    k.yyx*sceneSDF(p + k.yyx*h) +
    k.yxy*sceneSDF(p + k.yxy*h) +
    k.xxx*sceneSDF(p + k.xxx*h));
}
    
float shortestDistanceToSurface(vec3 eye, vec3 marchingDirection, float start, float end)
{
    float depth = start;
    for (int i = 0; i < MAX_MARCHING_STEPS; i++)
    {
        float dist = sceneSDF(eye + depth * marchingDirection);
        if (dist < EPSILON) 
        {
            return depth;
        }
        depth += dist;
        if (depth >= end) 
        {
            return end;
        }
    }
    return end;
}

vec4 objectPBRLighting(vec3 p, vec3 v){
    vec3 baseColor = vec3(0.8,0.7,0.9);
    float metalness = 0.0;
    float roughness = 0.5;
    float specular = 0.5;

    vec3 n = calcNormal(p);
    
    vec3 light = 20.0 * normalize(LightLoc);
    vec3 light_color = 20.0 * vec3(1.0,1.0,1.0);

    float falloffLength = dot(light - p, light - p);
    vec3 l = (light - p)/sqrt(falloffLength);//vector from sample point to light
    vec3 h = normalize(v + l);//normal vector of the microface at the sample point
    float a = roughness * roughness;
    float dotNL = clamp (dot (n, l), EPSILON, UPPER);
    float dotNV = clamp (dot (n, v), EPSILON, UPPER);
    float dotNH = clamp (dot (n, h), EPSILON, UPPER);
    float dotHV = clamp (dot (l, h), EPSILON, UPPER);

    float d = (dotNH * a * a - dotNH) * dotNH + 1.;
    float D = a * a / (PI * d * d);//GGX
    float Vis_SmithV = dotNL * (dotNV * (1. - a) + a);
    float Vis_SmithL = dotNV * (dotNL * (1. - a) + a);
    float Vis = 0.5 / (Vis_SmithV + Vis_SmithL);// VIS = G / (4. * dotNV * dotNL)
    vec3 F0 = mix(vec3(0.16 * specular * specular), baseColor, metalness);
    vec3 F = F0 + (1. - F0) * (1. - dotHV) * (1. - dotHV) * (1. - dotHV) * (1. - dotHV) * (1. - dotHV);
    vec3 kD = (1. - F) * (1. - metalness);
    vec3 f = kD * baseColor / PI + F * D * Vis;
    vec3 c = PI * f * light_color * dotNL * 17. / falloffLength + vec3(0.15);
    return vec4(c,1.0) ;
}

vec3 rayDirection(vec2 fragCoord) 
{
    vec3 outer = vec3((2.0 * fragCoord.x / Size.x) - 1.0,
                    (2.0 * fragCoord.y / Size.y) - 1.0,
                    -0.5);
    float w = dot(outer, PersInv[3].xyz) + PersInv[3][3];
    return normalize((((vec4(outer, 1.0) * PersInv).xyz / w) - vec3(ViewInv[0].w,ViewInv[1].w,ViewInv[2].w)));
}


void main()
{
    vec3 outer = vec3((2.0 * Size.x/2.0 / Size.x) - 1.0,
                    (2.0 * Size.y / Size.y) - 1.0,
                    -0.5);
    float w = dot(outer, PersInv[3].xyz) + PersInv[3][3];
    
    vec3 t = vec3(ViewInv[0].w,ViewInv[1].w,ViewInv[2].w);
    
    vec3 s = ( vec4(outer, 1.0)*PersInv ).xyz ;
    
    vec3 func = normalize(s / w- t);
    //vec3 dir = rayDirection(vec2(Size.x/2.0,Size.y/2.0));
    //dir = rayDirection(vec2(Size.x,Size.y));
    vec3 dir = rayDirection(position);
    float dist = shortestDistanceToSurface(CamLoc, dir, MIN_DIST, MAX_DIST);
    
    if (dist > MAX_DIST - EPSILON) {
        // Didn't hit anything
        fragColor = vec4(0.0, 0.0, 0.0, 0.0);
        fragColor = blender_srgb_to_framebuffer_space(fragColor);
        return;
    }
    
    vec3 p = CamLoc + dist * dir;
    
    fragColor = objectPBRLighting(p, -dir);
    fragColor = blender_srgb_to_framebuffer_space(fragColor);
}

'''


def rot(vec, dtheta, dphi):
    #takes list xyz (single coord)
    x = vec[0]
    y = vec[1]
    z = vec[2]
    r = math.sqrt(x * x + y * y + z * z)
    theta = math.atan2(y, x) + dtheta * math.pi / 180
    phi = math.acos(z / r) + dphi * math.pi / 180  #to degrees
    return (math.sin(phi) * math.cos(theta), math.sin(phi) * math.sin(theta),
            math.cos(phi))


config = {"size": [0, 0]}


def update_config():
    screen = bpy.context.window.screen
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    region3d = area.spaces[0].region_3d
                    config["size"] = [region.width, region.height]
                    inv_pers = region3d.perspective_matrix.inverted()
                    config["inv_pers_matrix"] = inv_pers.transposed()
                    inv_view = region3d.view_matrix.inverted()
                    config["inv_view_matrix"] = inv_view.transposed()
                    config["cam"] = inv_view.translation
                    config["light"] = mathutils.Vector(
                        rot(config["cam"], 30, -30))
                    # print(view3d_utils.region_2d_to_vector_3d(region,region3d,(region.width/2,region.height/2)))
                    # print(view3d_utils.region_2d_to_vector_3d(region,region3d,(0,0)))
                    # print(view3d_utils.region_2d_to_vector_3d(region,region3d,(region.width,0)))
                    # print(view3d_utils.region_2d_to_vector_3d(region,region3d,(region.width,region.height)))
                    # print(view3d_utils.region_2d_to_vector_3d(region,region3d,(0,region.height)))
                    # print(view3d_utils.region_2d_to_origin_3d(region,region3d,(region.width/2,region.height/2)))
                    # camp = view3d_utils.region_2d_to_origin_3d(region,region3d,(0,0))
                    # print(camp)
                    # print(region3d.view_location)
                    # print(region3d.window_matrix)
                    # print(region3d.view_matrix)
                    #print(region3d.view_matrix.inverted().translation)

                    #print(region3d.perspective_matrix.inverted()[3].xyz)

                    coord = [region.width / 2, region.height / 2]
                    out = Vector(
                        ((2.0 * coord[0] / region.width) - 1.0,
                         (2.0 * coord[1] / region.height) - 1.0, -0.5))
                    #print('out:',out)

                    w = out.dot(inv_pers[3].xyz) + inv_pers[3][3]

                    #print('w:',w)

                    view_vector = ((inv_pers @ out) / w) - inv_view.translation
                    view_vector.normalize()
                    #print(inv_pers)
                    #print(out)
                    #print(inv_pers @ out)
                    #print(inv_view.translation)
                    #print(view_vector)

                    #config["inv_view_matrix"] = region3d.view_matrix.to_3x3().inverted()
                    #vmat_inv = region3d.view_matrix.inverted()
                    # print(config["inv_view_matrix"])
                    #pmat = region3d.perspective_matrix @ vmat_inv
                    #config["lens"] = 2.0*math.atan(1.0/pmat[1][1])*180.0/math.pi
                    #config["cam"] = vmat_inv.translation
                    # print(config["cam"])
                    # print(camp)
                    print('\n')


vertices = ((0, 0), (600, 0), (0, 600), (600, 600))

indices = ((0, 1, 2), (2, 1, 3))

shader = gpu.types.GPUShader(v_, f_)
batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)


def tag_redraw_all_3dviews():

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


tag_redraw_all_3dviews()


def draw():
    shader.bind()
    update_config()
    [width, height] = config["size"]
    # print(width, height)
    shader.uniform_float("ViewInv", config["inv_view_matrix"])
    shader.uniform_float("PersInv", config["inv_pers_matrix"])
    shader.uniform_float("Size", (width, height))
    shader.uniform_float("CamLoc", config["cam"])
    shader.uniform_float("LightLoc", config["light"])
    # shader.uniform_float("ModelViewProjectionMatrix", config["pmatrix"])
    vertices = ((0, 0), (width, 0), (0, height), (width, height))
    batch = batch_for_shader(shader,
                             'TRIS', {"pos": vertices},
                             indices=indices)
    batch.draw(shader)


list = []
#list.append(bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW'))
#bpy.types.SpaceView3D.draw_handler_remove(list[0], 'WINDOW')

#tag_redraw_all_3dviews()

print(1)


def my_handler(scene):
    print("Frame Change", scene.frame_current)
    if scene.frame_current % 2 == 0:
        if len(list) == 0:
            list.append(
                bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW',
                                                       'POST_PIXEL'))
            tag_redraw_all_3dviews()
    else:
        if list:
            bpy.types.SpaceView3D.draw_handler_remove(list[0], 'WINDOW')
            del list[0]
            tag_redraw_all_3dviews()


bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(my_handler)
