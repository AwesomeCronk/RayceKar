#version 450 core
layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba32f, binding = 0) uniform image2D screen;

#define pi 3.1415926535897932384626

float degToRad(float deg) {return deg * pi / 180;}

float radToDeg(float rad) {return rad * 180 / pi;}


float sdfSphere(vec3 pos, vec4 rot)
{
    vec3 spherePos = vec3(0.0, 0.0, 0.0);
    float sphereRad = 0.5;
    return length(spherePos - pos) - sphereRad;
}

float sdfScene(vec3 pos)
{
    return sdfSphere(pos);
}


void main()
{
    ivec2 resolution = imageSize(screen);
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);  // Location of the pixel
    vec4 color = vec4(0.2, 0.2, 0.7, 1.0);          // Background color

    vec3 focalPoint = vec3(0.0, -5.0, 0.0); // Focal point of the camera
    float focalLength = 0.1;                // Distance from focal point to lens
    float fov = degToRad(70.0);             // Field of view (horizontal)

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
    float dstTotal = 0.0;
    float dstMax = 20.0;
    int maxSteps = 200;
    float thres = 0.01;
    for (int i=0; i < maxSteps; i++)
    {
        dstScene = sdfScene(rayPos);
        dstTotal += dstScene;
        rayPos += rayDir * dstScene;


        if (dstScene <= thres)
        {
            color = vec4(0.0, 0.8, 0.0, 1.0);
            break;
        }

        if (dstTotal >= dstMax)
        {
            color = vec4(0.5, 0.0, 0.0, 1.0);
            break;
        }
    }

    // color = vec4(dstTotal / dstMax, dstTotal / dstMax, dstTotal / dstMax, 1.0);

    // Final drawing of pixel
    imageStore(screen, pixel, color);
}