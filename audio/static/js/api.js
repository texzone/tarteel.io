var api = {

    get_ayah: function (callback) {
        // An endpoint returns a random ayah.
        $.get("/get_ayah", function (data) {
            callback.call(this, data);
        })
    },
    get_specific_ayah: function (surah, ayah, callback) {
        // An endpoint takes specific (surah & ayah) as params and returns that ayah.
        $.ajax(
            {
                type: "POST",
                url: "/get_ayah/",
                data: {surah, ayah},
                dataType: "json",
                success: function (data) {
                    callback.call(this, data);
                }
            }
        );
        return false;
    },

    // Uploading the recording file after each recitation.
    send_recording: function (audio, surah_num, ayah_num, hash_string, mode) {
        const recitationMode = mode === true ? "continuous" : "discrete";
        var fd = new FormData();
        fd.append('file', audio, surah_num + "_" + ayah_num + "_" + hash_string + ".wav");
        fd.append('surah_num', surah_num);
        fd.append('ayah_num', ayah_num);
        fd.append('hash_string', hash_string); // a hash comes in the ayah object that get returned from /get_ayah .
        fd.append('recitation_mode', recitationMode);
        $.ajaxQueue(
            {
                type: "POST",
                url: "/api/recordings/",
                data: fd,
                processData: false,
                contentType: false,
                complete: function (jqXHR, textStatus) {
                    console.log(textStatus);
                }
            }
        )
    },


    get_specific_ayah: function (surah_data, ayah_data, callback) {
        $.ajax(
            {
                type: "POST",
                url: "/get_ayah/",
                data: {
                    surah: surah_data,
                    ayah: ayah_data
                },
                dataType: "json",
                success: function (data) {
                    callback.call(this, data);
                }
            }
        );
        return false;
    },

    send_recording: function (audio, surah_num, ayah_num, hash_string, mode) {
        const recitationMode = mode === true ? "continuous" : "discrete";
        var fd = new FormData();
        fd.append('file', audio, surah_num + "_" + ayah_num + "_" + hash_string + ".wav");
        fd.append('surah_num', surah_num);
        fd.append('ayah_num', ayah_num);
        fd.append('hash_string', hash_string);
        fd.append('recitation_mode', recitationMode);
        $.ajax(
            {
                type: "POST",
                url: "/api/recordings/",
                data: fd,
                processData: false,
                contentType: false,
                complete: function (jqXHR, textStatus) {
                    console.log(textStatus);
                }
            }
        )
    }
};
