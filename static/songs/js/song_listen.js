const app = Vue.createApp({
    methods: {
        onTimeUpdateListener() {
            // change active line only if needed
            let current_line = this.lyrics_data[this.selected_index]
            let pl_time = document.querySelector("#player").currentTime * 1000  // milliseconds
            this.set_current_time(pl_time)

            if (!(current_line["start"] <= pl_time && current_line["end"] > pl_time)) {
                for (let [index, line_obj] of Object.entries(this.lyrics_data)) {
                    if (line_obj["start"] <= pl_time && line_obj["end"] > pl_time) {
                        this.set_selected_index(index)

                        // also scroll to make sure text is visible on screen
                        if (this.auto_scroll && this.selected_index >= this.scroll_num) {
                            // ! allow to disable, otherwise when editing times, is very ხელისშემშლელი
                            document.querySelectorAll("#lyrics > div")[this.selected_index - this.scroll_num].scrollIntoView()
                        }
                        break
                    }
                }
            }
        },
        set_selected_index(val) { this.selected_index = val },
        set_current_time(val) { this.current_time = val },

        decrease_line_length(index) {
            // user clicked on minus sign near line duration
            let delta = this.change_delta
            let new_end = this.lyrics_data[index].end - delta

            if (new_end >= this.lyrics_data[index]["start"]) {
                this.lyrics_data[index].end = new_end
                for (let elem of this.lyrics_data.slice(index + 1)) {
                    elem["start"] -= delta
                    elem["end"] -= delta
                }
            }

        },

        increase_line_length(index) {
            // user clicked on plus sign near line duration
            let delta = this.change_delta

            this.lyrics_data[index].end += delta
            for (let elem of this.lyrics_data.slice(index + 1)) {
                elem["start"] += delta
                elem["end"] += delta
            }
        },
        set_audio_time_at(new_val) {
            // it uses seconds, so...
            document.querySelector("#player").currentTime = new_val / 1000
        },

        save_data() {
            // add better/nice and more informative in ui to know if * is successfully saved and 
            // when to not close page when still updating...
            // if (this.is_loading){return}

            this.is_loading = true
            console.log("saving data", this.lyrics_data)

            fetch("", {
                method: "POST",
                body: JSON.stringify({
                    csrfmiddlewaretoken: document.querySelector("[name='csrfmiddlewaretoken']").value,
                    data: this.lyrics_data.map(elem => { return {s: elem.start, e:elem.end} })
                }),
                headers: { "Content-Type": "application/json" },
              })
                .then((res) => res.json())
                .then((res) => {
                //   this.keywords_stats_data = res["keywords_stats_data"];
                    console.log("Got data", res)
                    
                    if (res.success){
                        this.is_loading = false
                    }
                });
        },

        set_change_delta(new_val) {
            if (! typeof new_val === 'number') {
                new_val = new_val.target.value * 1000
            } else {
                new_val *= 1000
            }

            if (new_val >= 100 && new_val <= 10000) {
                this.change_delta = new_val
            } else (
                console.log("Sorry, ", new_val, "is not between 0.1 and 10 seconds")
            )
        },
    },
    data() {
        return {
            "audio_source": "",
            "youtube_image":"",
            "is_loading": false,
            "auto_scroll": false,
            "scroll_num": 4,
            "selected_index": 0,
            "current_time": 0,
            "change_delta": 100, // how fast/slow does click change line length
            "lyrics_data":[],
        }
    },

    template:
        `
        <div id="fixed_line_div">
            <img
                :src=youtube_image
                id="song_image_icon"
            />
            <div v-if="is_loading">
                <div class="spinner-border text-warning" role="status">
                    <span class="sr-only"></span>
                </div>
            </div>
            <div
                title="Press s to save"
                v-else
                id="save"
                @click="save_data"
            >🎵| Save |🎵 </div>

            <input 
                title="Press 0, 1 or 5 to change deltas easily"
                step="0.1" 
                type="number" 
                id="set_change_delta" 
                :value="change_delta / 1000" 
                @change="set_change_delta"
            />
            <div>
                <audio 
                    title="Press p to pause/continue"
                    id="player" 
                    :src="audio_source" 
                    controls @timeupdate='onTimeUpdateListener'
                ></audio>
            </div>
            <div id="selected_index_icon">
                {{ Number(selected_index) + 1}}
            </div>
        </div>
        <div id="lyrics">
            <div 
                v-for="(i, index) in lyrics_data"
                v-bind:class="{active: index == selected_index}"
                @click="set_audio_time_at(this.lyrics_data[index]['start'])"
            >
                <div class="lyrics_line">{{ i["text"]}}</div>

                <div class="plus_minus_outer_div">
                    <div v-on:click="decrease_line_length(index)" class="minus">-</div>
                    <div v-on:click="increase_line_length(index)" class="plus">+</div>
                </div>

                <div>{{ (Number(this.lyrics_data[index]['end'] - this.lyrics_data[index]['start']) / 1000).toFixed(1) }}</div>
                
                <progress 
                    v-if="index == selected_index"
                    :value=" current_time - this.lyrics_data[index]['start'] "
                    :max=" this.lyrics_data[index]['end'] - this.lyrics_data[index]['start'] " />
                <div v-else></div>

                <div v-if="index == selected_index" class="passed_time_div">{{ ((current_time - this.lyrics_data[index]['start']) / 1000).toFixed(1) }}</div>
                <div v-else></div>
            </div>
        </div>
                `,

    mounted: function () {
        let app_obj = this;
        // add info about this shortcuts somewhere to make our/others life easier...
        // later add key for enable/disabling auto scrolling

        let song_data = JSON.parse(document.querySelector("#song_data").value)

        app_obj.lyrics_data = song_data.lyrics_data
        app_obj.audio_source = song_data.audio_source
        app_obj.youtube_image = song_data.youtube_image

        console.log(song_data)


        // add start/stop event listeners
        window.addEventListener("keyup", function (event) {
            if (event.keyCode === 83) { // s key
                app_obj.save_data()
                
            }else if (event.keyCode === 76) { // l (el) - auto scroll on/off
                console.log(app_obj.auto_scroll)
                app_obj.auto_scroll = ! app_obj.auto_scroll
                console.log(app_obj.auto_scroll)

            } else if (event.keyCode == 80) { // p - pause/continue
                event.preventDefault()
                let player = document.querySelector("#player")
                player.paused ? player.play() : player.pause()

            } else if (event.keyCode == 49) { // 1 - switch delta to 1 seconds
                app_obj.set_change_delta(1)
            } else if (event.keyCode == 48) { // 0 - switch delta to 0.1 seconds
                app_obj.set_change_delta(0.1)
            } else if (event.keyCode == 53) { // 5 - switch delta to 5 seconds
                app_obj.set_change_delta(5)
            }
        }, false);
    }
})


