#version 440 core
// Compute shader `renderScene.glsl`
layout(local_size_x = 8, local_size_y = 8) in;
// layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba32f, binding = 0) uniform image2D screen;
layout(std430, binding = 1) buffer typeStorageBuffer {int widgetTypes[];};
layout(std430, binding = 2) buffer intStorageBuffer {int widgetInts[];};
layout(std430, binding = 3) buffer floatStorageBuffer {float widgetFloats[];};

void main()
{
    ivec2 resolution = imageSize(screen);
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);  // Location of the pixel
    vec4 color = vec4(0, 0, 0, 0);                  // Transparent - no widget

    int intPtr = 0;
    int floatPtr = 0;
    for (int i = 0; i < widgetTypes.length(); i++)
    {
        ivec2 widgetPos = ivec2(widgetInts[intPtr], widgetInts[intPtr + 1]);
        ivec2 widgetDim = ivec2(widgetInts[intPtr + 2], widgetInts[intPtr + 3]);
        if (all(greaterThan(pixel, widgetPos)) && all(lessThan(pixel, widgetPos + widgetDim)))
        {
            color = vec4(
                widgetFloats[floatPtr],
                widgetFloats[floatPtr + 1],
                widgetFloats[floatPtr + 2],
                1.0
            );
        }
        intPtr += 4;

    }

    if (color.w == 1)
    {
        imageStore(screen, pixel, color);
    }
}