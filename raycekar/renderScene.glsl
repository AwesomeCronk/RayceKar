// Compute shader `renderScene.glsl`
// This shader is a component of the RayceKar project and is intended to work with its rendering system
// https://github.com/AwesomeCronk/RayceKar

#version 440 core


layout(local_size_x = @{THREAD_GROUP_SIZE_X}, local_size_y = @{THREAD_GROUP_SIZE_Y}) in;
layout(rgba32f, binding = 0) uniform image2D screen;

layout(std430, binding = 1) buffer shapeTypeStorageBuffer   {int shapeTypes[];};
layout(std430, binding = 2) buffer shapeIntStorageBuffer    {int shapeInts[];};
layout(std430, binding = 3) buffer shapeFloatStorageBuffer  {float shapeFloats[];};

layout(std430, binding = 4) buffer lightTypStorageBuffer    {int lightTypes[];};
layout(std430, binding = 5) buffer lightFloatStorageBuffer  { float lightFloats[];};

layout(std430, binding = 6) buffer shapeContactsBuffer      {int contacts[];};


#define pi 3.1415926535897932384626

// Aliasing to make quaternions easier to figure out
#define quat vec4
#define n  x
#define ni y
#define nj z
#define nk w

// Shape IDs
# define idSphere 1
# define idBox 2

struct _contact {
    vec4 color;
    int id;
    vec3 pos;
    float dst;
};


//// Conversions ////
float degToRad(float deg) {return deg * pi / 180;}

float radToDeg(float rad) {return rad * 180 / pi;}

quat axisAngleToQuat(vec4 axisAngle)
{
    float halfAngle = axisAngle.w / 2;
    return quat(
        cos(halfAngle),
        axisAngle.x * sin(halfAngle),
        axisAngle.y * sin(halfAngle),
        axisAngle.z * sin(halfAngle)
    );
}

vec4 quatToAxisAngle(quat q)\
{
    return vec4(
        q.ni,
        q.nj,
        q.nk,
        acos(q.n) * 2
    );
}


//// Rotations ////
quat conjugateq(quat q) {return quat(q.n, -q.ni, -q.nj, -q.nk);}

quat multiplyqq(quat q0, quat q1)
{
    return quat(
        (q0.n  * q1.n ) - (q0.ni * q1.ni) - (q0.nj * q1.nj) - (q0.nk * q1.nk),
        (q0.n  * q1.ni) + (q0.ni * q1.n ) + (q0.nj * q1.nk) - (q0.nk * q1.nj),
        (q0.n  * q1.nj) + (q0.nj * q1.n ) + (q0.nk * q1.ni) - (q0.ni * q1.nk),
        (q0.n  * q1.nk) + (q0.nk * q1.n ) + (q0.ni * q1.nj) - (q0.nj * q1.ni)
    );
}

vec3 multiplyqv(quat q, vec3 v)
{
    quat vecQuat = quat(0, v.x, v.y, v.z);
    quat resultQuat = multiplyqq(multiplyqq(q, vecQuat), conjugateq(q));
    return vec3(resultQuat.ni, resultQuat.nj, resultQuat.nk);
}


//// SDFs ////
float sdfSphere(vec3 ray, vec3 pos, float radius)
{
    return length(pos - ray) - radius;
}

float sdfBox(vec3 ray, vec3 pos, quat rot, vec3 dimensions)
{
    rot = normalize(rot);             // Rotate by the inverse of rot to get rayRel
    quat rayRot = quat(rot.n, -rot.ni, -rot.nj, -rot.nk);
    vec3 rayRel = multiplyqv(rayRot, ray - pos);
    vec3 diff = abs(rayRel) - (dimensions * 0.5);    // Subtract half the dimensions to get a vector to the nearest corner
    // If a component of diff is <= 0, then rayRel is above the corresponding surface and not out
    // at a corner, so we cut that bit out to make the length add up
    if (all(lessThan(diff, vec3(0, 0, 0)))) return max(max(diff.x, diff.y), diff.z);
    else return length(vec3(max(diff.x, 0), max(diff.y, 0), max(diff.z, 0)));
}

float sdfInfPlane(vec3 rayPos, vec3 planePos)
{
    return rayPos.z - planePos.z;
}


//// CFs ////
vec4 cfSphere()
{
    return vec4(1, 0.2, 0.2, 1);
}

vec4 cfBox()
{
    return vec4(0.2, 0.2, 1, 1);
}

_contact resolvePixel(vec3 rayPos, vec3 rayDir)
{
    float dstScene;
    float dstTotal = 0;
    float dstMax = 7;
    int maxSteps = 200;
    float thres = 0.01;
    vec4 color = vec4(0.2, 0.2, 0.7, 1);    // Kind of a sky blue - steps limit exceeded
    int contactID = -1;

    for (int i=0; i < maxSteps; i++)
    {
        // Walk the buffers and render conditionally
        int intPtr = 0;
        int floatPtr = 8;
        float dstScene = dstMax;
        
        for (int id = 1; id < shapeTypes.length(); id++)
        {
            switch (shapeTypes[id])
            {
                case idSphere:
                    float dstSphere = sdfSphere(
                        rayPos,
                        // pos
                        vec3(
                            shapeFloats[floatPtr],
                            shapeFloats[floatPtr + 1],
                            shapeFloats[floatPtr + 2]
                        ),
                        // radius
                        shapeFloats[floatPtr + 3]
                    );
                    floatPtr += 4;
                    dstScene = min(dstScene, dstSphere);
                    break;

                case idBox:
                    float dstBox = sdfBox(
                        rayPos,
                        // pos
                        vec3(
                            shapeFloats[floatPtr],
                            shapeFloats[floatPtr + 1],
                            shapeFloats[floatPtr + 2]
                        ),
                        // rot
                        quat(
                            shapeFloats[floatPtr + 4],
                            shapeFloats[floatPtr + 5],
                            shapeFloats[floatPtr + 6],
                            shapeFloats[floatPtr + 7]
                        ),
                        // dimensions
                        vec3(
                            shapeFloats[floatPtr + 8],
                            shapeFloats[floatPtr + 9],
                            shapeFloats[floatPtr + 10]
                        )
                    );
                    floatPtr += 12;
                    dstScene = min(dstScene, dstBox);
                    break;
            }

            if (dstScene <= thres)
            {
                contactID = id;
                break;
            }
        }

        dstTotal += dstScene;
        rayPos += rayDir * dstScene;


        if (dstScene <= thres)
        {
            color = vec4(0, 0.8, 0, 1);     // Green - shape contact
            break;
        }

        if (dstTotal >= dstMax)
        {
            color = vec4(0.5, 0, 0.5, 1);   // This purple color - distance limit exceeded
            break;
        }
    }

    switch (shapeTypes[contactID])
    {
        case idSphere: color = cfSphere();
        case idBox: color = cfBox();
    }
    

    return _contact(color, contactID, rayPos, dstTotal);
}


void main()
{
    ivec2 resolution = imageSize(screen);
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);          // Location of the pixel
    
    _contact contact;
    vec4 color;
    
    if (shapeTypes[0] != 0) color = vec4(0.4, 0, 0, 1);     // Dark red - camera not defined
    else
    {
        vec3 cameraPos = vec3(shapeFloats[0], shapeFloats[1], shapeFloats[2]);
        quat cameraRot = quat(shapeFloats[4], shapeFloats[5], shapeFloats[6], shapeFloats[7]);

        vec3 focalPoint = cameraPos;    // Focal point of the camera
        float focalLength = 0.1;        // Distance from focal point to lens
        float fov = shapeFloats[3];     // Field of view (horizontal)

        // pixelSize is calculated from fov, focalLength, and resolution.x
        // sensorSize is calculated from pixelSize and resolution
        float pixelSize = (2 * tan(fov * 0.5) * focalLength) / float(resolution.x);   // Size of a pixel in the environment
        vec2 sensorSize = pixelSize * vec2(resolution);   // Size of the sensor in the environment

        // rayPos is calculated to be at the center of each pixel
        vec3 rayPos = focalPoint;
        // rayDir is calculated as a position offset, *not* a quaternion
        vec3 rayDir = normalize(
            vec3(
                ((0.5 + float(pixel.x)) * pixelSize) - (0.5 * sensorSize.x),
                focalLength,
                ((0.5 + float(pixel.y)) * pixelSize) - (0.5 * sensorSize.y)
            )
        );
        rayDir = multiplyqv(cameraRot, rayDir);     // Rotate the ray by cameraRot


        contact = resolvePixel(rayPos, rayDir);
        color = contact.color;

    }

    // Final drawing of pixel and data export
    imageStore(screen, pixel, color);
    contacts[pixel.x + (pixel.y * resolution.x)] = contact.id;
}