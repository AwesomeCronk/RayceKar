#version 440 core
// Compute shader `renderScene.glsl`
layout(local_size_x = @{THREAD_GROUP_SIZE_X}, local_size_y = @{THREAD_GROUP_SIZE_Y}) in;
layout(rgba32f, binding = 0) uniform image2D screen;
layout(std430, binding = 1) buffer typeStorageBuffer {int widgetTypes[];};
layout(std430, binding = 2) buffer intStorageBuffer {int widgetInts[];};
layout(std430, binding = 3) buffer floatStorageBuffer {float widgetFloats[];};

vec4 blend(vec4 a, vec4 b)
{
    return vec4(((a.xyz * a.w) + (b.xyz * b.w)), a.w + b.w);
}

vec4 clampColor(vec4 raw)
{
    if (raw.w > 1) return vec4(raw.xyz / raw.w, 1);
    else return raw;
}

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
                widgetFloats[floatPtr + 3]
            );
            
        }
        intPtr += 4;
    }

    color = clampColor(color);
    if (color.w == 1)
    {
        imageStore(screen, pixel, color);
    }
    else if (color.w > 0)
    {
        vec4 original = imageLoad(screen, pixel);
        imageStore(screen, pixel, clampColor(blend(original, color)));
    }
}