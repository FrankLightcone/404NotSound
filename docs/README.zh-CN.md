# 404NotSound

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://your-build-url) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[中文] | [English](../README.md)

**404NotFound集成了开源语音识别项目[SenseVoice](https://github.com/FunAudioLLM/SenseVoice)和[DeepSeek API](https://api-docs.deepseek.com/)，用于课堂或讲座记录，使用DeepSeek整理，输出Markdown格式总结**

[//]: # (![img_1.png]&#40;img_1.png&#41;{:height="50%" width="50%"})
<img src="img_1.png" width = "500" height = "610" alt="overview" align=center />

## 目录

*   [项目简介](#项目简介)
*   [快速开始](#快速开始)
    *   [客户端](#客户端)
    *   [服务器端](#服务器端)
*   [开发计划](#开发计划)

## 项目简介

正如项目名所言，404NotSound含蓄地代表了经常在课堂上发生的类似于“对不起，我没听清楚”的情况。本项目目前使用PySide6作为GUI框架开发，SenseVoice作为语音识别引擎，DeepSeek作为LLM整理引擎。

例如：
输入3Blue1Brown的视频（提取出音频，后续可能会考虑添加视频支持），原视频链接
[https://www.bilibili.com/video/BV1xmA2eMEFF](https://www.bilibili.com/video/BV1xmA2eMEFF)（Bilibili）
[https://youtu.be/LPZh9BOjkQs](https://youtu.be/LPZh9BOjkQs)（YouTube），
SenseVoice识别出的文本如下：
<details> 
<summary><font size="4" color="orange">展开识别文本</font></summary> 
<pre><code class="text-xl">Imagine you happen across a short movie script that describes a scene between a person and their AI assistant,
the script has what the person asks the AI, but the AI's response has been torn off.
Suppose you also have this powerful magical machine that can take any text and provide
a sensible prediction of what word comes next You could then finish the script by
feeding in what you have to the machine, seeing what it would predict to start
the AI's answer and then repeating this over and over with a growing script completing
the dialogue When you interact with a chatbot, this is exactly what's happening a large
language model is a sophisticated mathematical function that predicts what word comes
next for any piece.🎼of text instead of predicting one word with certainty, though, what
it does is assign a probability to all possible next words to build a chatbot What you do
is lay out some text that describes an interaction between a user and a hypothetical AI assistant
you add on whatever the user types in as the first part of that interaction and then you have the
model repeatedly predict the next word that such a hypothetical AI assistant would say in response
and that's what's presented to the user in doing,The output tends to look a lot more natural if
you allow it to select less likely words along the way at random, so what this means is even though
the model itself is deterministic, a given prompt typically gives a different answer each time it's
run.Models learn how to make these predictions by processing an enormous amount of text typically
pulled from the internet for a standard human to read the amount of text that was used to train GPT3,
for example, if they read nonstop 24/7, it would take over 2,600 years, larger models since then train
on much, much more.You can think of training a little bit like tuning the dials on a big machine, the
way that a language model behaves is entirely determined by these many different continuous values,
usually called parameters or weights.🎼Changing those parameters will change the probabilities that
the model gives for the next word on a given input, what puts the large in large language model is 
how they can have hundreds of billions of these parameters.No human ever deliberately sets those
parameters, instead they begin at random, meaning the model just outputs gibberish, but they are
repeatedly refined based on many example pieces of text.One of these training examples could be just
a handful of words, or it could be thousands, but in either case, the way this works is to pass in all
but the last word from that example into the model and compare the prediction that it makes with the
true last word from the example, an algorithm called back propagation is used to tweak all of the
parameters in such a way that it makes the model a little more likely to choose the true last word and
a little less likely to choose all the others.When you do this for many, many trillions of examples, not
only does the model start to give more accurate predictions on the training data, but it also starts to
make more reasonable predictions on text that it's never seen before.Given the huge number of parameters
and the enormous amount of training data, the scale of computation involved in training a large language
model is mind boggling.To illustrate, imagine that you could perform 1 billion editions and multiplications
every single second, how long do you think that it would take for you to do all of the operations involved
in training the largest language models?Do you think it would take a year, maybe something like 10,000
years, The answer is actually much more than that it's well over 100 million years.This is only part of
the story though This whole process is called pre-training The goal of auto completinglet a random passage
of text from the internet is very different from the goal of being a good AI assistant, to address this
chatbots undergo another type of training just as important called reinforcement learning with human feedback Workers flag unhelpful or problematic predictions and their corrections further change the model's parameters, making them more likely to give predictions that users prefer.Looking back at the pretraining though, this staggering amount of computation is only made possible by using special computer chips that are optimized for running many, many operations in parallel known as GPUs. However, not all language models can be easily parallelzed prior to 2017 Most language models would process text one word at a time, but then a team of researchers at Google introduced a new model known as the Transformer.Yeah.🎼Transformers don't read text from the start to the finish They soak it all in at once in parallel The very first step inside a transformer and most other language models for that matter is to associate each word with a long list of numbers The reason for this is that the training process only works with continuous values so you have to somehow encode language using numbers and each of these list of numbers may somehow encode the meaning of the corresponding word What makes transformers unique is their rely.On a special operation known asten.This operation gives all of these lists of numbers a chance to talk to one another and refine the meanings that they encode based on the context around, all done in parallel For example, the numbers encoding the word bank might be changed based on the context surrounding it to somehow encode the more specific notion of a river bank.Transformers typically also include a second type of operation known as a feed forwardward neural network, and this gives the model extra capacity to store more patterns about language learned during training.All of this data repeatedly flows through many different iterations of these two fundamental operations, and as it does so, the hope is that each list of numbers is enriched to encode whatever information might be needed to make an accurate prediction of what word follows in the passage.Yeah.At the end, one final function is performed on the last vector in this sequence, which now has had a chance to be influenced by all the other context from the input text, as well as everything the model learned during training to produce a prediction of the next word again, the model's prediction looks like a probability for every possible next word.🎼Yeah.Although researchers design the framework for how each of these steps work, it's important to understand that the specific behavior is an emergent phenomenon based on how those hundreds of billions of parameters are tuned during training. This makes it incredibly challenging to determine why the model makes the exact predictions that it does What you can see is that when you use large language model predictions to autocomplete a prompt. The words that it generates are uncannily fluent, fascinating and.Even useful.🎼If you're a new viewer and you're curious about more details on how transformers and attention work Boy do I have some material for you One option is to jump into a series I made about deep learning where we visualize and motivate the details of attention and all the other steps in a transformer but also on my second channel I just posted a talk that I gave a couple months ago about this topic for the company T and G in Munich Sometimes I actually prefer the content that I make as a casual talk rather than a produced video, but I leave it up to you which one of,Fel like the better follow on.</code>
</pre> </details>


原文本较长，向右滑动可查看更多

使用DeepSeek整理后，输出如下（纯文本输出，可切换Markdown格式输出）：

```markdown
讲座内容摘要：大型语言模型的工作原理
1. 核心主题
本次讲座的核心主题是**大型语言模型（Large Language Models, LLMs）**的工作原理，特别是它们如何通过预测下一个词来生成自然语言文本。讲座详细介绍了模型的训练过程、结构设计以及如何通过大量数据和计算资源来实现这些功能。

2. 主要知识点与结构
2.1 语言模型的基本功能
预测下一个词：大型语言模型的核心功能是预测给定文本的下一个词。它们通过为所有可能的词分配概率来实现这一点，而不是确定性地选择一个词。
生成自然语言：通过反复预测下一个词，模型可以生成连贯的对话或文本。为了使输出更自然，模型有时会随机选择概率较低的词。
2.2 模型的训练过程
预训练（Pre-training）：
模型通过处理大量文本（通常来自互联网）来学习预测下一个词。
例如，训练GPT-3所用的文本量，如果一个人24/7不间断阅读，需要超过2,600年才能完成。
训练过程涉及调整模型的参数（parameters/weights），这些参数决定了模型的行为。
通过**反向传播（backpropagation）**算法，模型不断优化参数，使其更可能预测正确的词。
强化学习与人类反馈（Reinforcement Learning with Human Feedback, RLHF）：
为了使模型更适合作为AI助手，模型会经过额外的训练阶段。人类工作者标记不准确或不合适的预测，并修正模型，使其更符合用户需求。
2.3 模型的规模与计算需求
参数数量：大型语言模型通常有数百亿个参数，这些参数通过训练不断调整。
计算规模：训练这些模型需要巨大的计算资源。例如，完成最大模型的训练操作，即使每秒进行10亿次运算，也需要超过1亿年。
硬件支持：训练过程依赖于GPU（图形处理单元），这些芯片能够并行处理大量运算。
2.4 Transformer架构
并行处理：与早期语言模型逐词处理不同，Transformer模型能够同时处理整个文本。
词嵌入（Word Embedding）：每个词被编码为一个长列表的数字，这些数字通过训练不断调整，以捕捉词的语义。
注意力机制（Attention Mechanism）：
Transformer的核心操作是注意力机制，它允许模型根据上下文动态调整词的编码。
例如，词“bank”的编码会根据上下文（如“river bank”或“bank account”）进行调整。
前馈神经网络（Feedforward Neural Network）：Transformer还包括前馈神经网络，用于存储更多语言模式。
2.5 模型的预测与输出
最终预测：在Transformer的最后一步，模型根据输入文本和训练中学到的知识，生成下一个词的概率分布。
涌现行为（Emergent Behavior）：模型的具体行为是由数百亿个参数在训练中调整的结果，这使得研究人员难以完全解释模型的预测逻辑。

3. 重要细节
训练数据量：GPT-3的训练数据量相当于一个人阅读2,600年的文本。
计算时间：训练最大模型所需的计算时间超过1亿年（假设每秒10亿次运算）。
注意力机制的作用：注意力机制使模型能够根据上下文动态调整词的语义编码。
强化学习的作用：通过人类反馈，模型能够生成更符合用户需求的响应。

4. 拓展与补充
Transformer的起源：Transformer架构由Google的研究团队于2017年提出，彻底改变了语言模型的处理方式。
注意力机制的可视化：讲座提到可以通过深度学习系列视频进一步了解注意力机制的工作原理。

5. 总结
本次讲座深入探讨了大型语言模型的工作原理，从预测下一个词的基本功能到复杂的训练过程和Transformer架构的设计。通过大量数据和计算资源，这些模型能够生成流畅且自然的语言文本，但其具体行为仍然是一个复杂的涌现现象，难以完全解释。
```

### 快速开始

#### 客户端

clone本项目，安装依赖，运行即可

```bash
git clone https://github.com/FrankLightcone/404NotSound.git
cd 404NotSound
pip install -r requirements.txt
python app.py
```
#### 服务器端
需要安装SenseVoice相关依赖，参考[SenseVoice](https://github.com/FunAudioLLM/SenseVoice)的安装步骤

运行SenseVoice服务端：
```bash
python api_key_server.py
```
根据具体情况在客户端中填写SenseVoice的API地址，首次运行会输出管理员API Key，持有此Key 可以通过如下命令创建新的API Key：
```bash
curl -k -X POST "https://<Your Server IP Address>:14612/admin/create_key" \
     -H "X-API-Key: <Your Server Admin API Key>" \
     -H "Content-Type: application/json" \
     -d '{}'
```

关于DeepSeek相关问题，参考[DeepSeek API](https://api-docs.deepseek.com/)文档


### 开发计划

- [x] 完成基本的GUI界面
- [ ] 支持视频输入
- [ ] 支持同时输入课程PPT
- [ ] 支持使用其他LLM模型
- [ ] 支持多轮对话