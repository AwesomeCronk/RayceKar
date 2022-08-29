#version 450 core
layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba32f, binding = 0) uniform image2D screen;

#define pi 3.1415926535897932384626

float degToRad(float deg) {return deg * pi / 180;}

float radToDeg(float rad) {return rad * 180 / pi;}


float sdfSphere(vec3 rayPos)
{
    vec3 spherePos = vec3(0, 0, 0);
    float sphereRad = 1;
    return length(spherePos - rayPos) - sphereRad;
}

float sdfBox(vec3 rayPos, vec3 boxPos, vec3 boxDim)
{
    // abs moves the ray to the same corner to make easy math
    // Subtract half the dimensions to get a vector to the nearest corner
    vec3 diff = abs(rayPos - boxPos) - (boxDim * 0.5);
    // If a component of diff is <= 0, then rayPos is above the corresponding surface and not out
    // at a corner, so we cut that bit out to make the length add up
    return length(vec3(max(diff.x, 0), max(diff.y, 0), max(diff.z, 0)));
}

float sdfInfPlane(vec3 rayPos, vec3 planePos)
{
    return rayPos.z - planePos.z;
}

float sdfScene(vec3 rayPos)
{
    // return sdfSphere(rayPos);
    float dstSphere = sdfSphere(rayPos);
    float dstBox = sdfBox(rayPos, vec3(1, 0, -0.5), vec3(1, 1, 1));
    float dstBox2 = sdfBox(rayPos, vec3(2, 0, 2), vec3(1, 1, 1));
    float dstPlane = sdfInfPlane(rayPos, vec3(0, 0, -1));

    return min(dstSphere, min(dstBox, min(dstBox2, dstPlane)));
}


void main()
{
    ivec2 resolution = imageSize(screen);
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);  // Location of the pixel
    vec4 color = vec4(0.2, 0.2, 0.7, 1);          // Background color

    vec3 focalPoint = vec3(0, -5, 0); // Focal point of the camera
    float focalLength = 0.1;                // Distance from focal point to lens
    float fov = degToRad(70);             // Field of view (horizontal)

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


    float dstScene;
    float dstTotal = 0;
    float dstMax = 7;
    int maxSteps = 200;
    float thres = 0.01;
    for (int i=0; i < maxSteps; i++)
    {
        dstScene = sdfScene(rayPos);
        dstTotal += dstScene;
        rayPos += rayDir * dstScene;


        if (dstScene <= thres)
        {
            color = vec4(0, 0.8, 0, 1);
            break;
        }

        if (dstTotal >= dstMax)
        {
            color = vec4(0.5, 0, 0, 1);
            break;
        }
    }

    color = vec4(pow(dstTotal / dstMax, 2), pow(dstTotal / dstMax, 2), pow(dstTotal / dstMax, 2), 1);

    // Final drawing of pixel
    imageStore(screen, pixel, color);
}