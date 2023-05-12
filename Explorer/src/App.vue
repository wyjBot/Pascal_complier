<template>
    <div class="c-container">
        <el-row class="c-header">
            <el-col :span="6">
                <div class="left title">Pascal-S 编译系统</div>
            </el-col>
            <el-col :span="11">
                <div class="center" >
                    <el-row>
                    <el-button type="info" plain @click="api_example" >example</el-button>
                    <el-button type="danger" plain @click="reset_clicked" >reset</el-button>
                    <el-button type="warning" plain @click="api_compile" >compile</el-button>
                    <el-button v-show="results.state==='suc'" type="primary" plain @click="api_generate">generate</el-button>
                    <el-button v-show="results.state==='suc'" type="success" plain @click="topbtn_execute_clicked" >execute</el-button>
                    </el-row>
                </div>
            </el-col>
            <el-col :span="3"></el-col>
            <el-col :span="4">
                <el-tabs v-model="currentTab" type="card" stretch>
                    <el-tab-pane  v-if="currentTab==='execute'" label="在线运行" name="execute"></el-tab-pane>
                    <el-tab-pane  v-if="currentTab==='cCode'" label="c语言代码 " name="cCode"></el-tab-pane>
                    <el-tab-pane  v-if="currentTab==='err'" name="err">
                        <template #label>
                            <el-badge class="errbdg"
                                :class="{ warning: results.error.length <= 0 }"
                                :value="computedErrors.length" :hidden="computedErrors.length <= 0"
                            > <span>错误和警告</span> </el-badge>
                        </template>
                    </el-tab-pane>
                    <el-tab-pane v-if="currentTab==='ast'" label="语法树" name="ast"></el-tab-pane>
                    <!-- <el-tab-pane label="符号表" name="sym"></el-tab-pane> -->
                    </el-tabs >
            </el-col>
        </el-row>
        <el-row class="c-content">
            <el-col :span="12">
                <MonacoEditor
                    ref="srcEditor"
                    class="c-editor ed-left"
                    theme="vs-dark"
                    language="pascal"
                    :value="codeSrc"
                    :options="{
                        DefaultEndOfLine: 1,
                        EndOfLinePreference: 1,
                    }"
                    @change="editorChange"
                    @editor-will-mount="editorWillMount"
                />
            </el-col>
            <el-col :span="12" style="border-left: 1px solid #444444">
                <div ref="treeCon" style="height: 100%">
                    <div v-show="currentTab === 'execute'" class="">
                    <div class="center title">运行输入</div>
                    <el-input
                        v-model="inputEx"
                        rows="9"
                        type="textarea"
                        placeholder="Please input"
                        @input="inputEx_change($event)"
                    />
                    <el-row :gutter="10" >
                    <el-col :span=8> <el-button type="info" plain  style="width:8vw" class='center' @click="cleanEx" >reset</el-button> </el-col>
                    <el-col :span=8> <el-button type="success" plain style="width:8vw" class='center' @click="api_execute">excute</el-button></el-col>
                    <el-col :span=8> <el-button type="default" plain  style="width:8vw" class='center' @click="help_clicked" >help</el-button> </el-col>
                    </el-row>
                        <!-- :disabled="true"  -->
                    <div class="center title">运行输出</div>

                    <el-input
                        v-model="outputEx"
                        rows=9
                        type="textarea"
                        readonly="true"
                        placeholder="执行结果"
                        @input="outputEx_change($event)"
                    />
                    </div>
                    <div v-show="currentTab === 'cCode'" class="ed-right-container">
                    <!-- <div v-show="true" class="" style="height: 100%"> -->
                        <!-- <MonacoEditor
                            ref="dstEditor"
                            class="c-editor ed-right"
                            theme="vs-dark"
                            language="c"
                            :value="results.code"
                            :options="{ readOnly: true }"
                        /> -->
                    <el-input
                        v-model="results.code"
                        rows="25"
                        type="textarea"
                        placeholder="生成代码"
                        readonly="true"
                        @input="outputEx_change($event)"
                    />
                    </div>
                    <div v-show="currentTab === 'err'" class="c-right">
                        <el-scrollbar :height="(treeConHeight || 300) - 1">
                            <el-empty
                                v-show="computedErrors.length <= 0"
                                description="0 Error(s), 0 Warning(s)"
                            ></el-empty>
                            <div v-for="(i, a) in computedErrors" :key="a" class="erritem">
                                <div class="left">
                                    <i
                                        class="codicon"
                                        :class="i.code.includes('W') ? 'codicon-warning' : 'codicon-error'"
                                    ></i>
                                </div>
                                <div class="right">
                                    <div class="message">
                                        {{ i.message }}
                                    </div>
                                    <div class="bottom">
                                        <div class="code">{{ i.code }}</div>
                                        <div class="line">Line {{ i.line }}, Col {{ i.column }}</div>
                                    </div>
                                </div>
                            </div>
                        </el-scrollbar>
                    </div>
                    <div v-show="currentTab === 'ast'" class="c-right">
                        <el-scrollbar :height="(treeConHeight || 300) - 1">
                            <div style="height: 20px"></div>
                            <el-tree
                                node-key="id"
                                :data="computedAstData.tree"
                                :default-expanded-keys="computedAstData.expanded"
                            >
                                <template #default="{ data }">
                                    <span class="el-tree-node__label">
                                        <span v-if="data.children">
                                            <span class="key object">{{ data.label }}</span>
                                        </span>
                                        <span v-else>
                                            <span class="key">{{ data.key }}</span>
                                            <span class="value jstype" :class="String(typeof data.value)">{{
                                                data.value
                                            }}</span>
                                        </span>
                                    </span>
                                </template>
                            </el-tree>
                        </el-scrollbar>
                    </div>
                    <div v-show="currentTab === 'sym'" class="c-right">
                        <el-scrollbar :height="(treeConHeight || 300) - 1">
                            <div style="height: 20px"></div>
                            <el-tree
                                node-key="id"
                                :data="computedSymTree.tree"
                                :default-expanded-keys="computedSymTree.expanded"
                                :indent="30"
                            >
                                <template #default="{ data }">
                                    <span class="el-tree-node__label">
                                        <span v-if="data.value">
                                            <!--常量-->
                                            <span class="symtype" :class="data.type.toLowerCase()">
                                                {{ data.type }}
                                            </span>
                                            <span class="key symkey">
                                                {{ data.token }}
                                            </span>
                                            <span class="value jstype" :class="String(typeof data.value.value)">
                                                {{ data.value.value }}
                                            </span>
                                        </span>
                                        <span v-else-if="typeof data.isArray === 'boolean'">
                                            <!--变量-->
                                            <span class="symtype" :class="data.type.toLowerCase()">
                                                {{ data.type }}
                                            </span>
                                            <span class="key symvar" :class="data.children ? 'object' : ''">
                                                {{
                                                    typeof data.token === 'string'
                                                        ? data.token
                                                        : data.token.ids.join('.')
                                                }}<span v-if="data.isArray">
                                                    <span v-for="(i, a) in data.size" :key="a">
                                                        <span style="color: #fff">[</span>
                                                        <span class="jstype number">{{ i }}</span>
                                                        <span style="color: #fff">]</span>
                                                    </span>
                                                </span>
                                            </span>
                                            <span v-if="data.isArray" class="value">
                                                start=<span v-for="(i, a) in data.start" :key="a">
                                                    <span style="color: #fff">[</span>
                                                    <span class="jstype number">{{ i }}</span>
                                                    <span style="color: #fff">]</span>
                                                </span>
                                            </span>
                                        </span>
                                        <span v-else-if="data.table">
                                            <span class="symtype" :class="data.type ? data.type.toLowerCase() : 'void'">
                                                {{ data.type || 'VOID' }}
                                            </span>
                                            <span class="key object">
                                                {{ data.token }}(<span v-for="i in data.table.params" :key="i">
                                                    <span
                                                        class="symtype functype"
                                                        :class="data.table.variables[i - 1].type.toLowerCase()"
                                                    >
                                                        {{ data.table.variables[i - 1].type }}
                                                    </span>
                                                    <span v-if="data.table.references[i - 1]" class="funcref">&</span>
                                                    <span class="jstype variable">{{
                                                        data.table.variables[i - 1].token
                                                    }}</span>
                                                    <span v-if="i < data.table.params" style="color: #fff"
                                                        >,
                                                    </span> </span
                                                >)
                                            </span>
                                        </span>
                                        <span v-else>
                                            <i v-if="data.icon" class="symicon" :class="data.icon"></i>
                                            {{ data.label }}
                                        </span>
                                    </span>
                                </template>
                            </el-tree>
                        </el-scrollbar>
                    </div>
                </div>
            </el-col>
        </el-row>
    </div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import { MarkerSeverity } from 'monaco-editor'
import { errStr } from './errors'
import { ISymbolTable, IErrorData } from './typing'
import { useElementSize, useEventListener, useDebounceFn } from '@vueuse/core'
import { defineComponent, computed, ref, h, watch, nextTick } from 'vue'
import MonacoEditor from 'vue-monaco'
import { ElNotification,ElMessage, ElMessageBox,Action } from 'element-plus'
// import func from 'vue-temp/vue-editor-bridge'
MonacoEditor.render = () => h('section')

export default defineComponent({
    name: 'App',
    components: { MonacoEditor },
    setup() {
        const lockApi = ref(false)
        const currentTab = ref('ast')
        const results = ref({
            id:'',
            srcCode: ``,
            code: ``,
            state:'reset',
            ast: {},
            symbolTable: {},
            error: [] as IErrorData[],
            warning: [] as IErrorData[],
        })
        const srcEditor = ref(null as any)
        const dstEditor = ref(null as any)
        const codeSrc = ref(``)
        const editorChange = (ev: unknown) => {
            if (typeof ev === 'string') {
                codeSrc.value = ev
            }
        }
        const inputEx_change=(e:unknown)=>{
            console.log("user are editing")
        }
        const outputEx_change=(e:unknown)=>{
            let a=3;
            a=a+3;
        }
        watch(codeSrc, async () => {
            await nextTick()
            await nextTick()
            if (srcEditor.value) {
                srcEditor.value.getEditor().getModel().setEOL(1)
            }
        })
        const debouncedEditorResize = useDebounceFn(() => {
            if (srcEditor.value) {
                srcEditor.value.getEditor().layout()
            }
            if (dstEditor.value) {
                dstEditor.value.getEditor().layout()
            }
        }, 100)
        useEventListener('resize', debouncedEditorResize, { passive: true })
        let monaco: any = null
        const editorWillMount = (m: any) => {
            monaco = m
        }
        const objectToElTree = (obj: any, id = { id: 0 }): any => {
            const elTree = []
            for (const key in obj) {
                if (Object.prototype.hasOwnProperty.call(obj, key)) {
                    const value = obj[key]
                    if (typeof value === 'object') {
                        elTree.push({
                            id: id.id++,
                            label: key,
                            children: objectToElTree(value, id),
                        })
                    } else {
                        elTree.push({
                            id: id.id++,
                            label: `${key}: ${value}`,
                            key: key,
                            value: value,
                        })
                    }
                }
            }
            return elTree
        }
        const computedAstData = computed(() => {
            const id = { id: 0 }
            const tree = objectToElTree(results.value.ast, id)
            const expanded = []
            for (const i of tree) {
                expanded.push(i.id)
                if (!i.children) continue
                for (const j of i.children) {
                    expanded.push(j.id)
                }
            }
            return {
                tree,
                expanded,
            }
        })
        const getSymTreeArray = (obj: ISymbolTable, id = { id: 0 }): any => {
            const elTree = []
            if (obj.constants) {
                elTree.push({
                    id: 'constant-' + id,
                    label: '全局常量',
                    icon: 'codicon codicon-symbol-constant',
                    children: obj.constants,
                })
            }
            if (obj.variables) {
                const v = obj.variables.map((e) => {
                    if (e.recordTable) {
                        id.id++
                        const c = getSymTreeArray(e.recordTable, id)
                        return {
                            ...e,
                            children: c[0].children,
                        }
                    }
                    return e
                })
                elTree.push({
                    id: 'variable-' + id,
                    label: '全局变量',
                    icon: 'codicon codicon-symbol-variable',
                    children: v,
                })
            }
            if (obj.subFunc) {
                const v = obj.subFunc.map((e) => {
                    if (e.table) {
                        id.id++
                        const c = getSymTreeArray(
                            {
                                constants: e.table.constants,
                                variables: e.table.variables?.slice((e.table as typeof e).params),
                            },
                            id,
                        )
                        c.forEach((e: any) => {
                            e.label = e.label.replace('全局', '局部')
                        })
                        return {
                            ...e,
                            children: c,
                        }
                    }
                    return e
                })
                elTree.push({
                    id: 'subfunc-' + id,
                    label: '函数',
                    icon: 'codicon codicon-symbol-function',
                    children: v,
                })
            }
            return elTree
        }
        const computedSymTree = computed(() => {
            const id = { id: 0 }
            const tree = getSymTreeArray(results.value.symbolTable as ISymbolTable, id)
            const expanded = []
            for (const i of tree) {
                expanded.push(i.id)
                if (!i.children) continue
                for (const j of i.children) {
                    expanded.push(j.id)
                }
            }
            return {
                tree,
                expanded,
            }
        })

        const computedErrors = computed(() => {
            return [...results.value.error, ...results.value.warning].map((e) => {
                return {
                    code: e.value,
                    line: e.line ,
                    column: e.column,
                    message: e.error,
                }
            })
        })
        const computedMarkers = computed(() => {
            const srcLine = codeSrc.value.split('\n')
            const dstLine = results.value.srcCode.split('\n')
            if (srcLine.length !== dstLine.length) {
                return []
            }
            return computedErrors.value.map((e) => {
                const line = dstLine[e.line - 1]
                const sline = srcLine[e.line - 1]
                if (!line || line.trim() !== sline.trim()) return {}
                const firstNonSpaceIndex = line.search(/\S/)
                return {
                    startLineNumber: e.line,
                    startColumn: (e.column || firstNonSpaceIndex) + 1,
                    endLineNumber: e.line,
                    // endColumn: e.end_column ? e.end_column : line.length + 1,
                    severity: e.code.includes('W') ? MarkerSeverity.Warning : MarkerSeverity.Error,
                    message: e.message,
                    code: e.code,
                }
            })
        })

        watch([computedMarkers, srcEditor], () => {
            if (!srcEditor.value || !monaco) return
            monaco.editor.setModelMarkers(srcEditor.value.getEditor().getModel(), 'pas2c', computedMarkers.value)
        })
        const toJsType = (type: string) => {
            switch (type) {
                case 'integer':
                case 'real':
                    return 'number'
                case 'char':
                    return 'string'
                case 'boolean':
                    return 'boolean'
                case 'record':
                    return 'object'
            }
            return type
        }

        // const precode = ref([] as { file_name: string; code: string }[])
        //     fetch('/example').then(async (res) => {
        //         if (!res.ok) {
        //             ElNotification.error({
        //                 title: '获取样例失败',
        //                 message: `${res.status} ${res.statusText}`,
        //             })
        //             return
        //         }
        //         const data = await res.json()
        //         precode.value = data
        //         precode.value = precode.value.sort((a, b) => {
        //             return a.file_name.localeCompare(b.file_name)
        //         })
        //     })
        // get example code
        function api_example(){
            fetch('/v2/example').then(async (res) => { 
                if (!res.ok) {
                    ElNotification.error({
                        title: '获取样例失败',
                        message: `${res.status} ${res.statusText}`,
                    })
                    return
                }
                const data = await res.text()
                codeSrc.value = data
                // precode.value = precode.value.sort((a, b) => {
                //     return a.file_name.localeCompare(b.file_name)
                // })
            })
        }
        const inputEx = ref('')
        const outputEx = ref('')
        const treeCon = ref(null as null | HTMLDivElement)
        const cleanEx = ()=>{
            inputEx.value=""
            outputEx.value=""
        }
        const { height: treeConHeight } = useElementSize(treeCon)

        function reset_clicked() {
            codeSrc.value=""
            results.value.state="reset"
            results.value.ast={}
            results.value.code=""
            currentTab.value="ast"
        }
        function topbtn_execute_clicked() {
            currentTab.value="execute"
        }
        function help_clicked(){
            ElMessageBox.alert("若出错,编译报错信息将直接显示在下方\n<br> 运行超时时间:3000ms", 'Title', {
                // if you want to disable its autofocus
                // autofocus: false,
                confirmButtonText: 'OK',
                dangerouslyUseHTMLString: true,
                callback: (action: Action) => {
                    ElMessage({
                        type: 'info',
                        dangerouslyUseHTMLString: true,
                        message: `感谢试用<br>2023 @编译原理课程设计-${action}`,
                    })
                }
            })
        }
        async function api_compile() {
            if (lockApi.value) return
            codeSrc.value = codeSrc.value.trim()
            const s = codeSrc.value
            if (s===''){ 
                ElNotification.error({
                    title: '出错了！',
                    duration: 2000,
                    message: "pascal源码不得为空",
                })
                return
            }
            lockApi.value = true
            try {
                const res = await fetch('/v2/compile', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'text/plain',
                    },
                    body: s,
                })
                if (!res.ok) {
                    throw new Error(`${res.status} ${res.statusText}`)
                }
                const data = await res.json()
                data.srcCode = s
                results.value = data
                if (results.value.state==='suc') {
                    currentTab.value='ast'
                } else {
                    currentTab.value='err'
                }
                console.log(results.value)
            } catch (e) {
                ElNotification.error({
                    title: '出错了！',
                    message: (e as Error).message,
                })
            }
            lockApi.value = false
        }
        async function api_generate() {
            await api_compile()
            currentTab.value="cCode"
        }

        async function api_execute() {
            if (lockApi.value) return
            lockApi.value = true
            codeSrc.value = codeSrc.value.trim()
            const srcLock= codeSrc.value
            const inputLock = inputEx.value
            try {
                const res = await fetch('/v2/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'text/plain',
                    },
                    body:JSON.stringify({
                        'id': results.value.id,
                        'input': inputEx.value,
                    })
                })
                if (!res.ok) {
                    throw new Error(`${res.status} ${res.statusText}`)
                }
                const data = await res.json()
                codeSrc.value = results.value.srcCode
                inputEx.value=inputLock
                outputEx.value=data.output
                console.log(data)
            } catch (e) {
                ElNotification.error({
                    title: '出错了！',
                    message: (e as Error).message,
                })
            }
            lockApi.value = false
        }
        return {
            inputEx,
            outputEx,
            cleanEx,
            codeSrc,
            help_clicked,
            reset_clicked,
            api_example,
            api_compile,
            api_generate,
            api_execute,
            inputEx_change,
            outputEx_change,
            results,
            editorChange,
            editorWillMount,
            currentTab,
            computedAstData,
            treeCon,
            treeConHeight,
            computedSymTree,
            toJsType,
            computedErrors,
            lockApi,
            srcEditor,
            dstEditor,
            topbtn_execute_clicked
        }
    },
})
</script>


<style lang="scss">
@import "./main.scss";
</style>