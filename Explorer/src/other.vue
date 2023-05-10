
                <el-row  style="border-left: 1px solid #444444" hidden='true'>
                    <div ref="treeCon" style="height: 100%">
                        <div v-show="currentTab === 'output'" class="ed-right-container">
                            <MonacoEditor
                                ref="dstEditor"
                                class="c-editor ed-right"
                                theme="vs-dark"
                                language="c"
                                :value="results.code"
                                :options="{ readOnly: true }"
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
                </el-row>