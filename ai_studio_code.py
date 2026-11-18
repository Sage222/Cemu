import os
import subprocess
import sys

REPO_DIR = r"C:\Users\SageDesk\Downloads\Cemu"
if os.path.exists(REPO_DIR):
    os.chdir(REPO_DIR)

print(f"Working in: {os.getcwd()}")


def run_cmd(cmd):
    print(f"> {' '.join(cmd)}")
    res = subprocess.run(cmd, text=True)
    if res.returncode != 0:
        sys.exit(res.returncode)


def patch_file(rel_path, replacements):
    full_path = os.path.join(os.getcwd(), rel_path.replace("/", os.sep))
    with open(full_path, "rb") as f:
        raw = f.read().decode("utf-8")
    has_crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    for idx, (old, new) in enumerate(replacements, 1):
        old_norm = old.replace("\r\n", "\n")
        new_norm = new.replace("\r\n", "\n")
        if old_norm not in text:
            raise RuntimeError(f"[{rel_path}] Hunk #{idx} target not found!")
        text = text.replace(old_norm, new_norm, 1)
    if has_crlf:
        text = text.replace("\n", "\r\n")
    with open(full_path, "wb") as f:
        f.write(text.encode("utf-8"))
    print(f"[OK] Patched {rel_path} ({len(replacements)} hunks)")


def main():
    # 1. Reset src/ to the clean upstream SSimco/Cemu commit while keeping .github/workflows/build_check.yml
    run_cmd(["git", "checkout", "8759323e5b", "--", "src/"])

    # 2. LatteDecompilerEmitGLSLHeader.hpp
    patch_file(
        "src/Cafe/HW/Latte/LegacyShaderDecompiler/LatteDecompilerEmitGLSLHeader.hpp",
        [
            (
                '\t\tif (decompilerContext->options->spirvInstrinsics.hasRoundingModeRTEFloat32)\n'
                '\t\t{\n'
                '\t\t\tsrc->add("#extension GL_EXT_spirv_intrinsics: enable" _CRLF);\n'
                '\t\t\tsrc->add("spirv_execution_mode(capabilities = [4467], extensions = [\\"SPV_KHR_float_controls\\"], 4462, 16);" _CRLF);\n'
                '\t\t\tsrc->add("spirv_execution_mode(capabilities = [4467], extensions = [\\"SPV_KHR_float_controls\\"], 4462, 32);" _CRLF);\n'
                '\t\t\tsrc->add("spirv_execution_mode(capabilities = [4467], extensions = [\\"SPV_KHR_float_controls\\"], 4462, 64);" _CRLF);\n'
                '\t\t}',
                '\t\tif (decompilerContext->options->spirvInstrinsics.hasRoundingModeRTEFloat32)\n'
                '\t\t{\n'
                '\t\t\tsrc->add("#extension GL_EXT_spirv_intrinsics: enable" _CRLF);\n'
                '\t\t\tsrc->add("spirv_execution_mode(capabilities = [4467], extensions = [\\"SPV_KHR_float_controls\\"], 4462, 32);" _CRLF);\n'
                '\t\t}',
            ),
            (
                '\t\t// TODO: fix this\n'
                '\t\tfor (uint32 i = 0; i < 32; i++)\n'
                '\t\t{\n'
                '\t\t\tif (!activePassParams[i])\n'
                '\t\t\t\tsrc->addFmt("layout(location = {0}) out vec4 dummyPassParameterSem{0};" _CRLF, i);\n'
                '\t\t}\n'
                '\n'
                '\t\tsrc->add("void dummyPassParamInit() {" _CRLF);\n'
                '\t\tfor (uint32 i = 0; i < 32; i++)\n'
                '\t\t{\n'
                '\t\t\tif (!activePassParams[i])\n'
                '\t\t\t\tsrc->addFmt("dummyPassParameterSem{} = vec4(0.0, 0.0, 0.0, 0.0);" _CRLF, i);\n'
                '\t\t}\n'
                '\t\tsrc->add("}" _CRLF);',
                '\t\tfor (sint32 i = 0; i < psInputTable->count; i++)\n'
                '\t\t{\n'
                '\t\t\tif (psInputTable->import[i].semanticId > LATTE_ANALYZER_IMPORT_INDEX_PARAM_MAX)\n'
                '\t\t\t\tcontinue;\n'
                '\t\t\tif (!activePassParams[i])\n'
                '\t\t\t{\n'
                '\t\t\t\tsrc->addFmt("layout(location = {}) ", i);\n'
                '\t\t\t\tif (psInputTable->import[i].isFlat)\n'
                '\t\t\t\t\tsrc->add("flat ");\n'
                '\t\t\t\tif (psInputTable->import[i].isNoPerspective)\n'
                '\t\t\t\t\tsrc->add("noperspective ");\n'
                '\t\t\t\tsrc->addFmt("out vec4 dummyPassParameterSem{};" _CRLF, i);\n'
                '\t\t\t}\n'
                '\t\t}\n'
                '\n'
                '\t\tsrc->add("void dummyPassParamInit() {" _CRLF);\n'
                '\t\tfor (sint32 i = 0; i < psInputTable->count; i++)\n'
                '\t\t{\n'
                '\t\t\tif (psInputTable->import[i].semanticId > LATTE_ANALYZER_IMPORT_INDEX_PARAM_MAX)\n'
                '\t\t\t\tcontinue;\n'
                '\t\t\tif (!activePassParams[i])\n'
                '\t\t\t\tsrc->addFmt("dummyPassParameterSem{} = vec4(0.0, 0.0, 0.0, 0.0);" _CRLF, i);\n'
                '\t\t}\n'
                '\t\tsrc->add("}" _CRLF);',
            ),
        ],
    )

    # 3. RendererShaderVk.cpp
    patch_file(
        "src/Cafe/HW/Latte/Renderer/Vulkan/RendererShaderVk.cpp",
        [
            ("defaultResource.maxVaryingFloats = 64;", "defaultResource.maxVaryingFloats = 128;"),
            ("defaultResource.maxVaryingVectors = 8;", "defaultResource.maxVaryingVectors = 32;"),
            ("defaultResource.maxVertexOutputVectors = 16;", "defaultResource.maxVertexOutputVectors = 32;"),
            ("defaultResource.maxFragmentInputVectors = 15;", "defaultResource.maxFragmentInputVectors = 32;"),
            ("defaultResource.maxVaryingComponents = 60;", "defaultResource.maxVaryingComponents = 128;"),
            ("defaultResource.maxVertexOutputComponents = 64;", "defaultResource.maxVertexOutputComponents = 128;"),
            ("defaultResource.maxGeometryInputComponents = 64;", "defaultResource.maxGeometryInputComponents = 128;"),
            (
                "uint32 spirvCacheMagic = GeneratePrecompiledCacheId();",
                "uint32 spirvCacheMagic = GeneratePrecompiledCacheId() ^ 0x50565232u;",
            ),
        ],
    )

    # 4. VulkanRenderer.cpp
    patch_file(
        "src/Cafe/HW/Latte/Renderer/Vulkan/VulkanRenderer.cpp",
        [
            (
                "\tdeviceFeatures.depthClamp = m_featureControl.deviceFeatures.depth_clamp;\n\tdeviceFeatures.depthBiasClamp = VK_TRUE;",
                "\tdeviceFeatures.depthClamp = m_featureControl.deviceFeatures.depth_clamp;\n\tdeviceFeatures.depthBiasClamp = deviceFeatures2.features.depthBiasClamp;",
            ),
            (
                "\t// enable VK_EXT_pipeline_robustness\n"
                "\tVkPhysicalDevicePipelineRobustnessFeaturesEXT pipelineRobustnessFeature{};\n"
                "\tif (m_featureControl.deviceExtensions.pipeline_robustness)\n"
                "\t{\n"
                "\t\tpipelineRobustnessFeature.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PIPELINE_ROBUSTNESS_FEATURES_EXT;\n"
                "\t\tpipelineRobustnessFeature.pNext = deviceExtensionFeatures;\n"
                "\t\tdeviceExtensionFeatures = &pipelineRobustnessFeature;\n"
                "\t\tpipelineRobustnessFeature.pipelineRobustness = VK_TRUE;\n"
                "\t}",
                "\t// enable VK_EXT_pipeline_robustness\n"
                "\tVkPhysicalDevicePipelineRobustnessFeaturesEXT pipelineRobustnessFeature{};\n"
                "\tif (m_featureControl.deviceExtensions.pipeline_robustness)\n"
                "\t{\n"
                "\t\tpipelineRobustnessFeature.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PIPELINE_ROBUSTNESS_FEATURES_EXT;\n"
                "\t\tpipelineRobustnessFeature.pNext = deviceExtensionFeatures;\n"
                "\t\tdeviceExtensionFeatures = &pipelineRobustnessFeature;\n"
                "\t\tpipelineRobustnessFeature.pipelineRobustness = VK_TRUE;\n"
                "\t}\n\n"
                "\t// enable VK_EXT_depth_clip_enable\n"
                "\tVkPhysicalDeviceDepthClipEnableFeaturesEXT depthClipFeature{};\n"
                "\tif (m_featureControl.deviceExtensions.depth_clip_enable)\n"
                "\t{\n"
                "\t\tdepthClipFeature.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DEPTH_CLIP_ENABLE_FEATURES_EXT;\n"
                "\t\tdepthClipFeature.pNext = deviceExtensionFeatures;\n"
                "\t\tdeviceExtensionFeatures = &depthClipFeature;\n"
                "\t\tdepthClipFeature.depthClipEnable = VK_TRUE;\n"
                "\t}",
            ),
            (
                "\tif (m_featureControl.deviceExtensions.transform_feedback)\n"
                "\t\tused_extensions.emplace_back(VK_EXT_TRANSFORM_FEEDBACK_EXTENSION_NAME);\n"
                "\tif (m_featureControl.deviceExtensions.depth_clip_enable)\n"
                "\t\tused_extensions.emplace_back(VK_EXT_DEPTH_CLIP_ENABLE_EXTENSION_NAME);",
                "\tif (m_featureControl.deviceExtensions.transform_feedback)\n"
                "\t\tused_extensions.emplace_back(VK_EXT_TRANSFORM_FEEDBACK_EXTENSION_NAME);",
            ),
            (
                "\t// transform feedback ringbuffer\n"
                "\tmemoryManager->CreateBuffer(LatteStreamout_GetRingBufferSize(), VK_BUFFER_USAGE_TRANSFORM_FEEDBACK_BUFFER_BIT_EXT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT | (m_featureControl.mode.useTFEmulationViaSSBO ? VK_BUFFER_USAGE_STORAGE_BUFFER_BIT : 0), 0, m_xfbRingBuffer, m_xfbRingBufferMemory);",
                "\t// transform feedback ringbuffer\n"
                "\tVkBufferUsageFlags xfbUsage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT;\n"
                "\tif (m_featureControl.deviceExtensions.transform_feedback)\n"
                "\t\txfbUsage |= VK_BUFFER_USAGE_TRANSFORM_FEEDBACK_BUFFER_BIT_EXT;\n"
                "\tif (m_featureControl.mode.useTFEmulationViaSSBO)\n"
                "\t\txfbUsage |= VK_BUFFER_USAGE_STORAGE_BUFFER_BIT;\n"
                "\tmemoryManager->CreateBuffer(LatteStreamout_GetRingBufferSize(), xfbUsage, 0, m_xfbRingBuffer, m_xfbRingBufferMemory);",
            ),
            (
                "\t// D24S8\n\tif (fmtProp.optimalTilingFeatures != 0) // todo - more restrictive check",
                "\t// D24S8\n\tif ((fmtProp.optimalTilingFeatures & VK_FORMAT_FEATURE_DEPTH_STENCIL_ATTACHMENT_BIT) != 0)",
            ),
            (
                "\t\tcase Latte::E_GX2SURFFMT::X24_G8_UINT:\n"
                "\t\t\t// used by Color Splash and Resident Evil\n"
                "\t\t\tformatInfoOut->vkImageFormat = VK_FORMAT_R8G8B8A8_UINT; // todo - should we use ABGR format?\n"
                "\t\t\tformatInfoOut->decoder = TextureDecoder_X24_G8_UINT::getInstance(); // todo - verify\n"
                "\t\tcase Latte::E_GX2SURFFMT::R32_X8_FLOAT:",
                "\t\tcase Latte::E_GX2SURFFMT::X24_G8_UINT:\n"
                "\t\t\t// used by Color Splash and Resident Evil\n"
                "\t\t\tformatInfoOut->vkImageFormat = VK_FORMAT_R8G8B8A8_UINT; // todo - should we use ABGR format?\n"
                "\t\t\tformatInfoOut->decoder = TextureDecoder_X24_G8_UINT::getInstance(); // todo - verify\n"
                "\t\t\tbreak;\n"
                "\t\tcase Latte::E_GX2SURFFMT::R32_X8_FLOAT:",
            ),
            ('fmt::format(L"{:016x}.bin"', 'fmt::format(L"{:016x}_pvr2.bin"'),
            ('fmt::format("{:016x}.bin"', 'fmt::format("{:016x}_pvr2.bin"'),
        ],
    )

    # 5. VulkanPipelineCompiler.cpp
    patch_file(
        "src/Cafe/HW/Latte/Renderer/Vulkan/VulkanPipelineCompiler.cpp",
        [
            (
                '\tgsSrc.append(fmt::format("gl_Position = gl_in[{}].gl_Position;\\r\\n", vIdx));\n'
                '\tgsSrc.append("EmitVertex();\\r\\n");',
                '\tfor (sint32 i = 0; i < psInputTable->count; i++)\n'
                '\t{\n'
                '\t\tif (psInputTable->import[i].semanticId > LATTE_ANALYZER_IMPORT_INDEX_PARAM_MAX)\n'
                '\t\t\tcontinue;\n'
                '\t\tbool exported = false;\n'
                '\t\tfor (uint32 j = 0; j < 32; j++)\n'
                '\t\t{\n'
                '\t\t\tif ((parameterMask & (1 << j)) && psInputTable->getVertexShaderOutParamSemanticId(latteRegister.GetRawView(), j) == psInputTable->import[i].semanticId)\n'
                '\t\t\t{\n'
                '\t\t\t\texported = true;\n'
                '\t\t\t\tbreak;\n'
                '\t\t\t}\n'
                '\t\t}\n'
                '\t\tif (!exported)\n'
                '\t\t\tgsSrc.append(fmt::format("dummyPassParameterSem{}Out = vec4(0.0);\\r\\n", i));\n'
                '\t}\n'
                '\tgsSrc.append(fmt::format("gl_Position = gl_in[{}].gl_Position;\\r\\n", vIdx));\n'
                '\tgsSrc.append("EmitVertex();\\r\\n");',
            ),
            (
                '\tgsSrc.append(fmt::format("gl_Position = gen4thVertex{}(gl_in[0].gl_Position, gl_in[1].gl_Position, gl_in[2].gl_Position);\\r\\n", variant));\n'
                '\tgsSrc.append("EmitVertex();\\r\\n");',
                '\tfor (sint32 i = 0; i < psInputTable->count; i++)\n'
                '\t{\n'
                '\t\tif (psInputTable->import[i].semanticId > LATTE_ANALYZER_IMPORT_INDEX_PARAM_MAX)\n'
                '\t\t\tcontinue;\n'
                '\t\tbool exported = false;\n'
                '\t\tfor (uint32 j = 0; j < 32; j++)\n'
                '\t\t{\n'
                '\t\t\tif ((parameterMask & (1 << j)) && psInputTable->getVertexShaderOutParamSemanticId(latteRegister.GetRawView(), j) == psInputTable->import[i].semanticId)\n'
                '\t\t\t{\n'
                '\t\t\t\texported = true;\n'
                '\t\t\t\tbreak;\n'
                '\t\t\t}\n'
                '\t\t}\n'
                '\t\tif (!exported)\n'
                '\t\t\tgsSrc.append(fmt::format("dummyPassParameterSem{}Out = vec4(0.0);\\r\\n", i));\n'
                '\t}\n'
                '\tgsSrc.append(fmt::format("gl_Position = gen4thVertex{}(gl_in[0].gl_Position, gl_in[1].gl_Position, gl_in[2].gl_Position);\\r\\n", variant));\n'
                '\tgsSrc.append("EmitVertex();\\r\\n");',
            ),
            (
                '\t\t\tif (f == 0)\n'
                '\t\t\t\tgsSrc.append(fmt::format(" vec4 passParameterSem{}In[];\\r\\n", vsSemanticId));\n'
                '\t\t\telse\n'
                '\t\t\t\tgsSrc.append(fmt::format(" vec4 passParameterSem{}Out;\\r\\n", vsSemanticId));\n'
                '\t\t}\n'
                '\t}',
                '\t\t\tif (f == 0)\n'
                '\t\t\t\tgsSrc.append(fmt::format(" vec4 passParameterSem{}In[];\\r\\n", vsSemanticId));\n'
                '\t\t\telse\n'
                '\t\t\t\tgsSrc.append(fmt::format(" vec4 passParameterSem{}Out;\\r\\n", vsSemanticId));\n'
                '\t\t}\n'
                '\t\tfor (sint32 i = 0; i < psInputTable->count; i++)\n'
                '\t\t{\n'
                '\t\t\tif (psInputTable->import[i].semanticId > LATTE_ANALYZER_IMPORT_INDEX_PARAM_MAX)\n'
                '\t\t\t\tcontinue;\n'
                '\t\t\tbool exported = false;\n'
                '\t\t\tfor (uint32 j = 0; j < 32; j++)\n'
                '\t\t\t{\n'
                '\t\t\t\tif ((parameterMask & (1 << j)) && psInputTable->getVertexShaderOutParamSemanticId(latteRegister.GetRawView(), j) == psInputTable->import[i].semanticId)\n'
                '\t\t\t\t{\n'
                '\t\t\t\t\texported = true;\n'
                '\t\t\t\t\tbreak;\n'
                '\t\t\t\t}\n'
                '\t\t\t}\n'
                '\t\t\tif (!exported)\n'
                '\t\t\t{\n'
                '\t\t\t\tgsSrc.append(fmt::format("layout(location = {}) ", i));\n'
                '\t\t\t\tif (psInputTable->import[i].isFlat)\n'
                '\t\t\t\t\tgsSrc.append("flat ");\n'
                '\t\t\t\tif (psInputTable->import[i].isNoPerspective)\n'
                '\t\t\t\t\tgsSrc.append("noperspective ");\n'
                '\t\t\t\tif (f == 0)\n'
                '\t\t\t\t\tgsSrc.append(fmt::format("in vec4 dummyPassParameterSem{}In[];\\r\\n", i));\n'
                '\t\t\t\telse\n'
                '\t\t\t\t\tgsSrc.append(fmt::format("out vec4 dummyPassParameterSem{}Out;\\r\\n", i));\n'
                '\t\t\t}\n'
                '\t\t}\n'
                '\t}',
            ),
            (
                "\trasterizer.depthClampEnable = VK_TRUE; // depth clamping is always enabled",
                "\trasterizer.depthClampEnable = vkRenderer->m_featureControl.deviceFeatures.depth_clamp ? VK_TRUE : VK_FALSE;",
            ),
            (
                "\tif (logicOp == Latte::LATTE_CB_COLOR_CONTROL::E_LOGICOP::COPY)",
                "\tif (logicOp == Latte::LATTE_CB_COLOR_CONTROL::E_LOGICOP::COPY || !VulkanRenderer::GetInstance()->m_featureControl.deviceFeatures.logic_op)",
            ),
        ],
    )

    # 6. VulkanRendererCore.cpp
    patch_file(
        "src/Cafe/HW/Latte/Renderer/Vulkan/VulkanRendererCore.cpp",
        [
            (
                "\t// barrier here\n\tif (writeFlushRequired)\n\t{\n\t\tVkMemoryBarrier memoryBarrier{};",
                "\t// barrier here\n\tif (writeFlushRequired)\n\t{\n\t\tif (m_state.activeRenderpassFBO != nullptr)\n\t\t\tdraw_endRenderPass();\n\t\tVkMemoryBarrier memoryBarrier{};",
            ),
            (
                "\tbool overridePassReuse = m_state.hasRenderSelfDependency && (GetConfig().vk_accurate_barriers || m_state.activePipelineInfo->neverSkipAccurateBarrier);\n"
                "\n"
                "\tif (!overridePassReuse && m_state.activeRenderpassFBO == fboVk)\n"
                "\t{\n"
                "\t\tif (m_state.descriptorSetsChanged)\n"
                "\t\t\tsync_inputTexturesChanged();\n"
                "\t\treturn;\n"
                "\t}\n"
                "\tdraw_endRenderPass();\n"
                "\tif (m_state.descriptorSetsChanged)\n"
                "\t\tsync_inputTexturesChanged();",
                "\tbool overridePassReuse = m_state.hasRenderSelfDependency;\n"
                "\n"
                "\tif (!overridePassReuse && m_state.activeRenderpassFBO == fboVk)\n"
                "\t{\n"
                "\t\tif (m_state.descriptorSetsChanged)\n"
                "\t\t\tsync_inputTexturesChanged();\n"
                "\t\tif (m_state.activeRenderpassFBO == fboVk)\n"
                "\t\t\treturn;\n"
                "\t}\n"
                "\telse\n"
                "\t{\n"
                "\t\tdraw_endRenderPass();\n"
                "\t\tif (m_state.descriptorSetsChanged)\n"
                "\t\t\tsync_inputTexturesChanged();\n"
                "\t}",
            ),
        ],
    )

    # 7. VulkanSurfaceCopy.cpp
    patch_file(
        "src/Cafe/HW/Latte/Renderer/Vulkan/VulkanSurfaceCopy.cpp",
        [
            (
                "\tVKRObjectRenderPass* vkObjRenderPass = new VKRObjectRenderPass(attachmentInfo, 1);",
                "\tVKRObjectRenderPass* vkObjRenderPass = new VKRObjectRenderPass(attachmentInfo, state.destinationTexture->isDepth ? 0 : 1);",
            ),
        ],
    )

    # 8. VulkanQuery.cpp
    patch_file(
        "src/Cafe/HW/Latte/Renderer/Vulkan/VulkanQuery.cpp",
        [
            (
                "\tvkCmdBeginQuery(m_rendererVk->m_state.currentCommandBuffer, m_rendererVk->m_occlusionQueries.queryPool, newQueryIndex, VK_QUERY_CONTROL_PRECISE_BIT);",
                "\tvkCmdBeginQuery(m_rendererVk->m_state.currentCommandBuffer, m_rendererVk->m_occlusionQueries.queryPool, newQueryIndex, m_rendererVk->m_featureControl.deviceFeatures.occlusion_query_precise ? VK_QUERY_CONTROL_PRECISE_BIT : 0);",
            ),
        ],
    )

    # 9. SwapchainInfoVk.cpp
    patch_file(
        "src/Cafe/HW/Latte/Renderer/Vulkan/SwapchainInfoVk.cpp",
        [
            (
                "\tcreate_info.oldSwapchain = nullptr;\n\tcreate_info.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT;",
                "\tcreate_info.oldSwapchain = nullptr;\n\tcreate_info.imageUsage = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | (details.capabilities.supportedUsageFlags & VK_IMAGE_USAGE_TRANSFER_DST_BIT);",
            ),
            (
                "\tcreateInfo.compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;",
                "\tVkCompositeAlphaFlagBitsKHR compositeAlpha = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR;\n"
                "\tif (!(swapchainSupport.capabilities.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR))\n"
                "\t{\n"
                "\t\tif (swapchainSupport.capabilities.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR)\n"
                "\t\t\tcompositeAlpha = VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR;\n"
                "\t\telse if (swapchainSupport.capabilities.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR)\n"
                "\t\t\tcompositeAlpha = VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR;\n"
                "\t\telse if (swapchainSupport.capabilities.supportedCompositeAlpha & VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR)\n"
                "\t\t\tcompositeAlpha = VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR;\n"
                "\t}\n"
                "\tcreateInfo.compositeAlpha = compositeAlpha;",
            ),
        ],
    )

    # 10. VKRMemoryManager.cpp
    patch_file(
        "src/Cafe/HW/Latte/Renderer/Vulkan/VKRMemoryManager.cpp",
        [
            (
                "\tVkMappedMemoryRange flushedRange{};\n"
                "\tflushedRange.sType = VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE;\n"
                "\tflushedRange.memory = uploadReservation.vkMem;\n"
                "\tflushedRange.offset = uploadReservation.bufferOffset;\n"
                "\tflushedRange.size = uploadReservation.size;",
                "\tconst VkDeviceSize atomSize = 64;\n"
                "\tconst VkDeviceSize alignedOffset = uploadReservation.bufferOffset & ~(atomSize - 1);\n"
                "\tconst VkDeviceSize alignedEnd = ((uploadReservation.bufferOffset + uploadReservation.size) + atomSize - 1) & ~(atomSize - 1);\n"
                "\tVkMappedMemoryRange flushedRange{};\n"
                "\tflushedRange.sType = VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE;\n"
                "\tflushedRange.memory = uploadReservation.vkMem;\n"
                "\tflushedRange.offset = alignedOffset;\n"
                "\tflushedRange.size = alignedEnd - alignedOffset;",
            ),
            (
                "\t\tVkMappedMemoryRange flushedRange{};\n"
                "\t\tflushedRange.sType = VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE;\n"
                "\t\tflushedRange.memory = uploadReservation->vkMem;\n"
                "\t\tflushedRange.offset = uploadReservation->bufferOffset;\n"
                "\t\tflushedRange.size = uploadReservation->size;",
                "\t\tconst VkDeviceSize atomSize = 64;\n"
                "\t\tconst VkDeviceSize alignedOffset = uploadReservation->bufferOffset & ~(atomSize - 1);\n"
                "\t\tconst VkDeviceSize alignedEnd = ((uploadReservation->bufferOffset + uploadReservation->size) + atomSize - 1) & ~(atomSize - 1);\n"
                "\t\tVkMappedMemoryRange flushedRange{};\n"
                "\t\tflushedRange.sType = VK_STRUCTURE_TYPE_MAPPED_MEMORY_RANGE;\n"
                "\t\tflushedRange.memory = uploadReservation->vkMem;\n"
                "\t\tflushedRange.offset = alignedOffset;\n"
                "\t\tflushedRange.size = alignedEnd - alignedOffset;",
            ),
        ],
    )

    # 11. Commit and push to trigger GitHub Actions
    run_cmd(["git", "add", "-A"])
    run_cmd(
        [
            "git",
            "commit",
            "-m",
            "Fix 3D shader VS exports, RoundingModeRTE, depthClipEnable, and SPIR-V cache for Pixel 10 Pro",
        ]
    )
    run_cmd(["git", "push", "origin", "android-port"])
    print("\n[SUCCESS] All patches applied and pushed to GitHub Actions!")


if __name__ == "__main__":
    main()